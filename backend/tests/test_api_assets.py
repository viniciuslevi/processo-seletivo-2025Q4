"""
Testes de integração para as rotas da API de Assets
"""
import pytest


class TestAssetRoutes:
    """Testes para as rotas de Asset"""
    
    def test_create_asset_success(self, client, auth_headers, created_owner, sample_asset_data):
        """Testa criação bem-sucedida de asset"""
        asset_data = {**sample_asset_data, "owner": created_owner["id"]}
        response = client.post("/integrations/asset", json=asset_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == sample_asset_data["name"]
        assert data["category"] == sample_asset_data["category"]
        assert data["owner"] == created_owner["id"]
    
    def test_create_asset_owner_not_found(self, client, auth_headers, sample_asset_data):
        """Testa erro ao criar asset com owner inexistente"""
        asset_data = {
            **sample_asset_data, 
            "owner": "00000000-0000-0000-0000-000000000000"
        }
        response = client.post("/integrations/asset", json=asset_data, headers=auth_headers)
        
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]
    
    def test_create_asset_missing_field(self, client, auth_headers, created_owner):
        """Testa erro com campo obrigatório faltando"""
        data = {
            "name": "Aeronave Boeing 737",
            "owner": created_owner["id"]
            # category faltando
        }
        response = client.post("/integrations/asset", json=data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_create_asset_name_too_long(self, client, auth_headers, created_owner):
        """Testa erro com nome muito longo"""
        data = {
            "name": "A" * 141,  # Máximo é 140
            "category": "Aeronave",
            "owner": created_owner["id"]
        }
        response = client.post("/integrations/asset", json=data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_get_asset_success(self, client, auth_headers, created_asset):
        """Testa busca bem-sucedida de asset por ID"""
        response = client.get(f"/integrations/asset/{created_asset['id']}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_asset["id"]
        assert data["name"] == created_asset["name"]
    
    def test_get_asset_not_found(self, client, auth_headers):
        """Testa busca de asset inexistente"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/integrations/asset/{fake_id}", headers=auth_headers)
        
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]
    
    def test_list_assets_empty(self, client, auth_headers):
        """Testa listagem quando não há assets"""
        response = client.get("/integrations/assets", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_assets_with_data(self, client, auth_headers, created_asset):
        """Testa listagem com assets existentes"""
        response = client.get("/integrations/assets", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == created_asset["id"]
    
    def test_list_assets_pagination(self, client, auth_headers, created_owner, sample_asset_data):
        """Testa paginação da listagem"""
        # Criar 5 assets
        for i in range(5):
            data = {
                "name": f"Asset {i}",
                "category": sample_asset_data["category"],
                "owner": created_owner["id"]
            }
            client.post("/integrations/asset", json=data, headers=auth_headers)
        
        # Primeira página
        response = client.get("/integrations/assets?skip=0&limit=2", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 2
        
        # Segunda página
        response = client.get("/integrations/assets?skip=2&limit=2", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 2
    
    def test_update_asset_success(self, client, auth_headers, created_asset):
        """Testa atualização bem-sucedida de asset"""
        update_data = {"name": "Aeronave Boeing 777"}
        response = client.put(
            f"/integrations/asset/{created_asset['id']}", 
            json=update_data
        , headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Aeronave Boeing 777"
        assert data["category"] == created_asset["category"]  # Não mudou
    
    def test_update_asset_not_found(self, client, auth_headers):
        """Testa atualização de asset inexistente"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"name": "Aeronave Boeing 777"}
        response = client.put(f"/integrations/asset/{fake_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_update_asset_owner_not_found(self, client, auth_headers, created_asset):
        """Testa atualização com owner inexistente"""
        update_data = {"owner": "00000000-0000-0000-0000-000000000000"}
        response = client.put(
            f"/integrations/asset/{created_asset['id']}", 
            json=update_data
        , headers=auth_headers)
        
        assert response.status_code == 404
        assert "Owner" in response.json()["detail"]
    
    def test_update_asset_name_too_long(self, client, auth_headers, created_asset):
        """Testa atualização com nome muito longo"""
        update_data = {"name": "A" * 141}
        response = client.put(
            f"/integrations/asset/{created_asset['id']}", 
            json=update_data
        , headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_delete_asset_success(self, client, auth_headers, created_asset):
        """Testa deleção bem-sucedida de asset"""
        response = client.delete(f"/integrations/asset/{created_asset['id']}", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Verificar que foi deletado
        response = client.get(f"/integrations/asset/{created_asset['id']}", headers=auth_headers)
        assert response.status_code == 404
    
    def test_delete_asset_not_found(self, client, auth_headers):
        """Testa deleção de asset inexistente"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(f"/integrations/asset/{fake_id}", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_asset_owner_relationship(self, client, auth_headers, created_owner, sample_asset_data):
        """Testa relacionamento entre asset e owner"""
        # Criar asset
        asset_data = {**sample_asset_data, "owner": created_owner["id"]}
        response = client.post("/integrations/asset", json=asset_data, headers=auth_headers)
        assert response.status_code == 201
        asset = response.json()
        
        # Verificar que owner existe
        response = client.get(f"/integrations/owner/{asset['owner']}", headers=auth_headers)
        assert response.status_code == 200
        owner = response.json()
        assert owner["id"] == created_owner["id"]
