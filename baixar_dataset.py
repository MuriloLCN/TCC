"""
Script para realizar o download do dataset 'aes_enem_dataset'

https://huggingface.co/datasets/kamel-usp/aes_enem_dataset/tree/main
"""
from datasets import load_dataset
# import pandas as pd
from pathlib import Path

if __name__ == "__main__":
    pastas = [
        # "JBCS2025",
        # "PROPOR2024",
        # "gradesThousand",
        # "sourceAOnly",
        "sourceAWithGraders",
        "sourceB"
    ]
    
    output_dir = Path("redacoes_enem_original")
    output_dir.mkdir(parents=True, exist_ok=True)

    for diretorio in pastas:
        print(f"Baixando subset: {diretorio}...")
        dataset = load_dataset("kamel-usp/aes_enem_dataset", diretorio)
        
        subset_dir = output_dir / diretorio
        subset_dir.mkdir(parents=True, exist_ok=True)

        # print(dataset)

        for split in dataset.keys():
            df = dataset[split].to_pandas()
            file_path = subset_dir / f"{split}.csv"
            df.to_csv(file_path, index=False)
            print(f"Salvo: {file_path}")

    print("Download completo")
