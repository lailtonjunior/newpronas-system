from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models, schemas
import pandas as pd
from typing import IO

def search_items(db: Session, query: str, skip: int = 0, limit: int = 100):
    search_query = f"%{query}%"
    return db.query(models.CatalogItem).filter(
        or_(
            models.CatalogItem.name.ilike(search_query),
            models.CatalogItem.description.ilike(search_query)
        )
    ).offset(skip).limit(limit).all()

def ingest_renem_data_from_csv(db: Session, csv_file: IO[bytes]):
    try:
        # Pular as primeiras linhas de cabeçalho informativo no CSV
        df = pd.read_csv(csv_file, skiprows=6, encoding='utf-8', sep=',')
        
        # Renomear colunas para corresponder ao nosso modelo
        df.rename(columns={
            'Cod. Item': 'item_code',
            'Item': 'name',
            'Definição': 'description',
            'R$ Valor Sugerido': 'suggested_price'
        }, inplace=True)
        
        items_to_add = []
        for _, row in df.iterrows():
            # Limpeza de dados
            price_str = row.get('suggested_price')
            price = None
            if pd.notna(price_str):
                try:
                    price = float(str(price_str).replace('.', '').replace(',', '.'))
                except (ValueError, TypeError):
                    price = None
            
            item_data = schemas.CatalogItemCreate(
                name=row.get('name'),
                description=row.get('description'),
                item_code=str(row.get('item_code')),
                suggested_price=price,
                source="RENEM",
                item_type="Equipamento"
            )
            
            db_item = models.CatalogItem(**item_data.dict())
            items_to_add.append(db_item)
        
        db.bulk_save_objects(items_to_add)
        db.commit()
        return {"status": "success", "items_ingested": len(items_to_add)}
    except Exception as e:
        db.rollback()
        print(f"Error ingesting RENEM data: {e}")
        return {"status": "error", "detail": str(e)}