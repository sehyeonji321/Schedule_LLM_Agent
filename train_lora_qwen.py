# train_lora_qwen.py

# 1. 설치 (한 번만 실행)
# pip install transformers datasets peft accelerate bitsandbytes trl

# python train_lora_qwen.py --resume_from_checkpoint ./results/qwen2.5-3b-lora/checkpoint-XXX XXX만 번호로수정해서쓰기


import os
import json
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer

# -----------------------------
# 1. 경로 & 환경설정
# -----------------------------
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # GPU 지정 (예: 0번만 사용)

MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
OUTPUT_DIR = "/home/aikusrv04/schedule_llm/JSH/results/qwen2.5-3b-lora"

DATA_PATH = "./data/train.jsonl"  # JSONL 하나만 준비하면 됨


# -----------------------------
# 2. 토크나이저
# -----------------------------
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token  # Qwen 호환

# -----------------------------
# 3. 데이터셋 로드 & 분할
# -----------------------------
dataset = load_dataset("json", data_files={"train": DATA_PATH})["train"]

# train/val 9:1 분할
dataset = dataset.train_test_split(test_size=0.1, seed=42)
train_dataset = dataset["train"]
val_dataset = dataset["test"]

# 프롬프트 포맷
def format_example(example):
    return f"""사용자 입력: {example['input']}
출력은 반드시 JSON만. 다음 스키마를 따르세요.
{json.dumps(example['output'], ensure_ascii=False, default=str)}"""

def tokenize(example):
    prompt = format_example(example)
    return tokenizer(prompt, truncation=True, max_length=1024)

train_tokenized = train_dataset.map(tokenize, remove_columns=train_dataset.column_names)
val_tokenized = val_dataset.map(tokenize, remove_columns=val_dataset.column_names)


# -----------------------------
# 4. 모델 로드 (QLoRA with BitsAndBytesConfig)
# -----------------------------
from transformers import BitsAndBytesConfig

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    quantization_config=quant_config
)

# -----------------------------
# 5. LoRA 설정
# -----------------------------
peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules=["q_proj","v_proj","k_proj","o_proj"]  # Qwen 권장
)
model = get_peft_model(model, peft_config)

# -----------------------------
# 6. 학습 설정
# -----------------------------
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=16,
    learning_rate=1e-4,
    num_train_epochs=3,
    logging_steps=50,
    do_eval=True,           # ✅ 추가
    eval_steps=200,         # 평가 주기
    save_strategy="steps",  # (구버전도 지원)
    save_steps=200,
    fp16=True,
    report_to=[]            # "none" 대신 빈 리스트
)


# -----------------------------
# 7. Trainer 실행
# -----------------------------
trainer = SFTTrainer(
    model=model,
    train_dataset=train_tokenized,
    eval_dataset=val_tokenized,
    tokenizer=tokenizer,
    args=training_args,
)

trainer.train()

# -----------------------------
# 8. 저장
# -----------------------------
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("✅ LoRA 파인튜닝 완료! 결과:", OUTPUT_DIR)