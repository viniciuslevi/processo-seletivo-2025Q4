from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse
from app.services.asset_service import AssetService
from app.db.sessions import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/integrations", tags=["Assets"])


@router.post(
    "/asset",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar um novo ativo",
    description="Cria um novo ativo no banco de dados. O ID é gerado automaticamente."
)
async def create_asset(
    asset: AssetCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> AssetResponse:
    """
    Cria um novo ativo com os seguintes campos obrigatórios:
    
    - **name**: Nome do ativo (máximo 140 caracteres)
    - **category**: Categoria do ativo (máximo 60 caracteres)
    - **owner**: ID do responsável (UUID)
    
    O ID do ativo é gerado automaticamente pelo sistema.
    """
    try:
        # Verificar se o owner existe
        from app.services.owner_service import OwnerService
        owner = OwnerService.get_owner(db, asset.owner)
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Owner com ID {asset.owner} não encontrado"
            )
        
        db_asset = AssetService.create_asset(db, asset)
        return AssetResponse.model_validate(db_asset)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/asset/{asset_id}",
    response_model=AssetResponse,
    summary="Buscar ativo por ID",
    description="Retorna os dados de um ativo específico pelo ID."
)
async def get_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> AssetResponse:
    """
    Busca um ativo pelo ID.
    
    Retorna 404 se o ativo não for encontrado.
    """
    db_asset = AssetService.get_asset(db, asset_id)
    if not db_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset com ID {asset_id} não encontrado"
        )
    return AssetResponse.model_validate(db_asset)


@router.get(
    "/assets",
    response_model=List[AssetResponse],
    summary="Listar todos os ativos",
    description="Retorna uma lista de todos os ativos cadastrados."
)
async def list_assets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> List[AssetResponse]:
    """
    Lista todos os ativos com paginação.
    
    - **skip**: Número de registros a pular (padrão: 0)
    - **limit**: Número máximo de registros a retornar (padrão: 100)
    """
    assets = AssetService.get_assets(db, skip=skip, limit=limit)
    return [AssetResponse.model_validate(asset) for asset in assets]


@router.put(
    "/asset/{asset_id}",
    response_model=AssetResponse,
    summary="Atualizar ativo",
    description="Atualiza os dados de um ativo existente."
)
async def update_asset(
    asset_id: str,
    asset: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> AssetResponse:
    """
    Atualiza um ativo existente.
    
    Apenas os campos fornecidos serão atualizados.
    Retorna 404 se o ativo não for encontrado.
    """
    try:
        # Se estiver atualizando o owner, verificar se existe
        if asset.owner:
            from app.services.owner_service import OwnerService
            owner = OwnerService.get_owner(db, asset.owner)
            if not owner:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Owner com ID {asset.owner} não encontrado"
                )
        
        db_asset = AssetService.update_asset(db, asset_id, asset)
        if not db_asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset com ID {asset_id} não encontrado"
            )
        return AssetResponse.model_validate(db_asset)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/asset/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar ativo",
    description="Remove um ativo do banco de dados."
)
async def delete_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Deleta um ativo pelo ID.
    
    Retorna 404 se o ativo não for encontrado.
    """
    deleted = AssetService.delete_asset(db, asset_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset com ID {asset_id} não encontrado"
        )
    return None

