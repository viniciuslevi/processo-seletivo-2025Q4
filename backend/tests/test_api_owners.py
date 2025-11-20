"""
Testes de integração para as rotas da API de Owners
"""
import pytest


class TestOwnerRoutes:
    """Testes para as rotas de Owner"""
    
    def test_create_owner_success(self, client, sample_owner_data, auth_headers):
        """Testa criação bem-sucedida de owner"""
        response = client.post(
            "/integrations/owner",
            json=sample_owner_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == sample_owner_data["name"]
        assert data["email"] == sample_owner_data["email"]
        assert data["phone"] == sample_owner_data["phone"]
    
    def test_create_owner_duplicate_email(self, client, created_owner, sample_owner_data, auth_headers):
        """Testa erro ao criar owner com email duplicado"""
        # Tentar criar outro owner com mesmo email
        response = client.post(
            "/integrations/owner",
            json=sample_owner_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Email já cadastrado" in response.json()["detail"]
    
    def test_create_owner_invalid_email(self, client, auth_headers):
        """Testa erro com email inválido"""
        data = {
            "name": "João da Silva",
            "email": "email-invalido",
            "phone": "+55 11 98765-4321"
        }
        response = client.post(
            "/integrations/owner",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_create_owner_missing_field(self, client, auth_headers):
        """Testa erro com campo obrigatório faltando"""
        data = {
            "name": "João da Silva",
            "phone": "+55 11 98765-4321"
            # email faltando
        }
        response = client.post(
            "/integrations/owner",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_get_owner_success(self, client, created_owner, auth_headers):
        """Testa busca bem-sucedida de owner por ID"""
        response = client.get(
            f"/integrations/owner/{created_owner['id']}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_owner["id"]
        assert data["name"] == created_owner["name"]
    
    def test_get_owner_not_found(self, client, auth_headers):
        """Testa busca de owner inexistente"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(
            f"/integrations/owner/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]
    
    def test_list_owners_empty(self, client, auth_headers):
        """Testa listagem quando não há owners"""
        response = client.get("/integrations/owners", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_owners_with_data(self, client, created_owner, auth_headers):
        """Testa listagem com owners existentes"""
        response = client.get("/integrations/owners", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == created_owner["id"]
    
    def test_list_owners_pagination(self, client, sample_owner_data, auth_headers):
        """Testa paginação da listagem"""
        # Criar 5 owners
        for i in range(5):
            data = {**sample_owner_data, "email": f"owner{i}@empresa.com"}
            client.post("/integrations/owner", json=data, headers=auth_headers)
        
        # Primeira página
        response = client.get(
            "/integrations/owners?skip=0&limit=2",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert len(response.json()) == 2
        
        # Segunda página
        response = client.get(
            "/integrations/owners?skip=2&limit=2",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert len(response.json()) == 2
    
    def test_update_owner_success(self, client, created_owner, auth_headers):
        """Testa atualização bem-sucedida de owner"""
        update_data = {"phone": "+55 11 99999-9999"}
        response = client.put(
            f"/integrations/owner/{created_owner['id']}", 
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "+55 11 99999-9999"
        assert data["name"] == created_owner["name"]  # Não mudou
    
    def test_update_owner_not_found(self, client, auth_headers):
        """Testa atualização de owner inexistente"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"phone": "+55 11 99999-9999"}
        response = client.put(
            f"/integrations/owner/{fake_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_update_owner_invalid_email(self, client, created_owner, auth_headers):
        """Testa atualização com email inválido"""
        update_data = {"email": "email-invalido"}
        response = client.put(
            f"/integrations/owner/{created_owner['id']}", 
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_delete_owner_success(self, client, created_owner, auth_headers):
        """Testa deleção bem-sucedida de owner"""
        response = client.delete(
            f"/integrations/owner/{created_owner['id']}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verificar que foi deletado
        response = client.get(
            f"/integrations/owner/{created_owner['id']}",
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_delete_owner_not_found(self, client, auth_headers):
        """Testa deleção de owner inexistente"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(
            f"/integrations/owner/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_delete_owner_cascades_to_assets(self, client, created_owner, created_asset, auth_headers):
        """Testa que deletar owner deleta seus assets (CASCADE)"""
        owner_id = created_owner["id"]
        asset_id = created_asset["id"]
        
        # Deletar owner
        response = client.delete(
            f"/integrations/owner/{owner_id}",
            headers=auth_headers
        )
        assert response.status_code == 204
        
        # Verificar que asset também foi deletado
        response = client.get(
            f"/integrations/asset/{asset_id}",
            headers=auth_headers
        )
        assert response.status_code == 404
