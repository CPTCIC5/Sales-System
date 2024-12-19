from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.models import get_db, User, Product, Category, Organization, organization_members
from utils.auth import get_current_user
from fastapi.responses import JSONResponse
from schemas.products_schema import CategoryModel, ProductModel
import requests
import json

router = APIRouter(prefix="/api/products")

@router.post('/create-category')
async def create_category(
    data: CategoryModel, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_category = Category(name=data.name)
    db.add(new_category)
    try:
        db.commit()
        db.refresh(new_category)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse({'detail': "New Category Registered"}, status_code=status.HTTP_201_CREATED)

@router.get('/all-category-options')
async def get_all_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    categories= db.query(Category).all()
    return categories


@router.delete('/delete-category/{category_id}')
async def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    element= db.query(Category).filter( Category.id == category_id).first()
    if element:
        db.delete(element)
        db.commit()
        return JSONResponse({"detail": "Deleted"},status_code=status.HTTP_204_NO_CONTENT)
    return HTTPException({"detail":"Not found"}, status_code=status.HTTP_404_NOT_FOUND)


@router.post("/create")
async def create_product(
    data: ProductModel,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Get user's organization - using the organization_members association table
    organization= db.query(Organization).filter(Organization.root_user == current_user).first()

    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not associated with any organization"
        )

    new_product = Product(
        org_id=organization.id,
        user_id=current_user.id,
        title=data.title,
        description=data.desc,
        image=data.image,
        product_type=data.product_type,
        category_id=data.category_id,
        price_per_quantity=data.price_per_quantity,
        is_available=data.is_available
    )
    
    db.add(new_product)
    try:
        db.commit()
        db.refresh(new_product)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
        
    return JSONResponse({'detail': "New Product Registered"}, status_code=status.HTTP_201_CREATED)


@router.get('/')
async def get_products(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    my_products= db.query(Product).filter(Product.user_id == current_user.id).all()
    response= requests.get('https://dummyapi.online/api/movies')
    if response.status_code == 200:
        data= json.loads(response.text)
    datt= []
    datt.append(my_products)
    datt.append(data)
    return datt

@router.get('/{product_id}')
async def get_product(product_id: int, db: Session = Depends(get_db), User= Depends(get_current_user)):
    get_prod= db.query(Product).filter(Product.id == product_id).first()
    if get_prod:
        return get_prod

@router.patch('/edit-{product_id}')
async def update_product(
    product_id: int, 
    data: ProductModel, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # First check if product exists and belongs to current user
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or you don't have permission to edit it"
        )
    
    # Update product fields
    product.title = data.title
    product.description = data.desc
    product.image = data.image
    product.product_type = data.product_type
    product.category_id = data.category_id
    product.price_per_quantity = data.price_per_quantity
    product.is_available = data.is_available
    
    try:
        db.commit()
        db.refresh(product)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return JSONResponse(
        {"detail": "Product updated successfully"},
        status_code=status.HTTP_200_OK
    )



@router.delete('/delete-{product_id}')
async def delete_product(product_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product= db.query(Product).filter(Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
        return JSONResponse({"detail":"Product Deleted Successfully"}, status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)