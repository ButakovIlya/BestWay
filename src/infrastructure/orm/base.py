# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from typing import List, Type

# from . import models, schemas

# class BaseViewSet:
#     model: Type[models.Base]
#     schema_read: Type[schemas.BaseModel]
#     schema_create: Type[schemas.BaseModel]
#     schema_update: Type[schemas.BaseModel]
#     prefix: str
#     tags: list

#     def __init__(self):
#         self.router = APIRouter(prefix=self.prefix, tags=self.tags)

#         self.router.add_api_route("/", self.list_items, response_model=List[self.schema_read], methods=["GET"])
#         self.router.add_api_route("/{item_id}", self.get_item, response_model=self.schema_read, methods=["GET"])
#         self.router.add_api_route("/", self.create_item, response_model=self.schema_read, methods=["POST"])
#         self.router.add_api_route("/{item_id}", self.update_item, response_model=self.schema_read, methods=["PUT"])
#         self.router.add_api_route("/{item_id}", self.delete_item, methods=["DELETE"])

#     def list_items(self, db: Session = Depends(get_db)):
#         return db.query(self.model).all()

#     def get_item(self, item_id: int, db: Session = Depends(get_db)):
#         obj = db.query(self.model).filter(self.model.id == item_id).first()
#         if not obj:
#             raise HTTPException(status_code=404, detail="Item not found")
#         return obj

#     def create_item(self, item: schemas.BaseModel, db: Session = Depends(get_db)):
#         db_obj = self.model(**item.dict())
#         db.add(db_obj)
#         db.commit()
#         db.refresh(db_obj)
#         return db_obj

#     def update_item(self, item_id: int, item: schemas.BaseModel, db: Session = Depends(get_db)):
#         db_obj = db.query(self.model).filter(self.model.id == item_id).first()
#         if not db_obj:
#             raise HTTPException(status_code=404, detail="Item not found")
#         for field, value in item.dict().items():
#             setattr(db_obj, field, value)
#         db.commit()
#         db.refresh(db_obj)
#         return db_obj

#     def delete_item(self, item_id: int, db: Session = Depends(get_db)):
#         db_obj = db.query(self.model).filter(self.model.id == item_id).first()
#         if not db_obj:
#             raise HTTPException(status_code=404, detail="Item not found")
#         db.delete(db_obj)
#         db.commit()
#         return {"detail": "Deleted"}
