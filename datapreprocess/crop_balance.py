from pathlib import Path
import shutil
import random

# ==========================
# 설정
# ==========================
SRC = Path("helmet_cls")      # helmet_cls 또는 vest_cls
DST = Path("helmet_cls_balanced")

SPLITS = ["train", "val", "test"]

# ==========================
# 클래스 이름
# ==========================
MINORITY = "no_helmet"
MAJORITY = "helmet"

# vest용이라면 아래처럼만 바꾸면 됨
# MINORITY = "no_safety_vest"
# MAJORITY = "safety_vest"

# ==========================
# 목표 비율
# majority = minority * TARGET_RATIO
# ==========================
TARGET_RATIO = 1.5

IMAGE_EXTS = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]

random.seed(42)


def list_images(folder):
    imgs = []

    for ext in IMAGE_EXTS:
        imgs.extend(folder.glob(f"*{ext}"))

    return imgs


def copy_folder(src, dst):
    if dst.exists():
        shutil.rmtree(dst)

    shutil.copytree(src, dst)


def balance_split(split):

    minority_dir = DST / split / MINORITY
    majority_dir = DST / split / MAJORITY

    minority_imgs = list_images(minority_dir)
    majority_imgs = list_images(majority_dir)

    minority_count = len(minority_imgs)
    majority_count = len(majority_imgs)

    target_majority = int(minority_count * TARGET_RATIO)

    print(f"\n[{split}]")
    print(f"{MINORITY}: {minority_count}")
    print(f"{MAJORITY}: {majority_count}")
    print(f"목표 {MAJORITY}: {target_majority}")

    if majority_count <= target_majority:
        print("삭제 필요 없음")
        return

    remove_count = majority_count - target_majority

    random.shuffle(majority_imgs)

    remove_imgs = majority_imgs[:remove_count]

    for img in remove_imgs:
        img.unlink()

    print(f"삭제된 {MAJORITY}: {remove_count}")


def count_final():

    print("\n====== 최종 개수 ======")

    for split in SPLITS:

        print(f"\n[{split}]")

        for cls in [MINORITY, MAJORITY]:

            cnt = len(list_images(DST / split / cls))

            print(f"{cls:<20}: {cnt}")


def main():

    copy_folder(SRC, DST)

    for split in SPLITS:
        balance_split(split)

    count_final()

    print("\n완료")


if __name__ == "__main__":
    main()