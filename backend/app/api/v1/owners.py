from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.owner import OwnerCreate, OwnerUpdate, OwnerResponse
from app.services.owner_service import OwnerService
from app.db.sessions import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/integrations", tags=["Owners"])


@router.post(
    "/owner",
    response_model=OwnerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar um novo responsável",
    description="Cria um novo responsável no banco de dados. O ID é gerado automaticamente."
)
async def create_owner(
    owner: OwnerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> OwnerResponse:
    """
    Cria um novo responsável com os seguintes campos obrigatórios:
    
    - **name**: Nome completo (máximo 140 caracteres)
    - **email**: Email corporativo (máximo 140 caracteres, deve ser único)
    - **phone**: Telefone (máximo 20 caracteres)
    
    O ID do responsável é gerado automaticamente pelo sistema.
    """
    try:
        db_owner = OwnerService.create_owner(db, owner)
        return OwnerResponse.model_validate(db_owner)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/owner/{owner_id}",
    response_model=OwnerResponse,
    summary="Buscar responsável por ID",
    description="Retorna os dados de um responsável específico pelo ID."
)
async def get_owner(
    owner_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> OwnerResponse:
    """
    Busca um responsável pelo ID.
    
    Retorna 404 se o responsável não for encontrado.
    """
    db_owner = OwnerService.get_owner(db, owner_id)
    if not db_owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Owner com ID {owner_id} não encontrado"
        )
    return OwnerResponse.model_validate(db_owner)


@router.get(
    "/owners",
    response_model=List[OwnerResponse],
    summary="Listar todos os responsáveis",
    description="Retorna uma lista de todos os responsáveis cadastrados."
)
async def list_owners(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> List[OwnerResponse]:
    """
    Lista todos os responsáveis com paginação.
    
    - **skip**: Número de registros a pular (padrão: 0)
    - **limit**: Número máximo de registros a retornar (padrão: 100)
    """
    owners = OwnerService.get_owners(db, skip=skip, limit=limit)
    return [OwnerResponse.model_validate(owner) for owner in owners]


@router.put(
    "/owner/{owner_id}",
    response_model=OwnerResponse,
    summary="Atualizar responsável",
    description="Atualiza os dados de um responsável existente."
)
async def update_owner(
    owner_id: str,
    owner: OwnerUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> OwnerResponse:
    """
    Atualiza um responsável existente.
    
    Apenas os campos fornecidos serão atualizados.
    Retorna 404 se o responsável não for encontrado.
    """
    try:
        db_owner = OwnerService.update_owner(db, owner_id, owner)
        if not db_owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Owner com ID {owner_id} não encontrado"
            )
        return OwnerResponse.model_validate(db_owner)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/owner/{owner_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar responsável",
    description="Remove um responsável e todos os seus ativos relacionados do banco de dados (cascade delete)."
)
async def delete_owner(
    owner_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Deleta um responsável pelo ID.
    
    **ATENÇÃO**: Esta operação também deletará todos os ativos associados a este responsável (cascade delete).
    
    Retorna 404 se o responsável não for encontrado.
    """
    deleted = OwnerService.delete_owner(db, owner_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Owner com ID {owner_id} não encontrado"
        )
    return None
