import pytest
from fastapi.testclient import TestClient

from database import Base, engine, SessionLocal
from main import app
from utils import API_KEYS


@pytest.fixture(scope="session", autouse=True)
def create_db():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(scope="function", autouse=True)
def db_session():

    connection = engine.connect()
    transaction = connection.begin()

    session = SessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture
def real_header():
    return {"X-API-Key": "tenant_a"}


@pytest.fixture
def fake_header():
    return {"X-API-Key": "tenant_faker"}


@pytest.fixture
def tools():
    return [
        {"name": "calculator", "description": "Calculator tool"},
        {"name": "search", "description": "Search tool"},
    ]


@pytest.fixture
def agent1():
    return {
        "name": "Research Agent",
        "role": "Research Assistant",
        "description": "Helps with research tasks",
        "tool_ids": []
    }


@pytest.fixture
def agent2():
    return {
        "name": "Test Agent",
        "role": "Tester",
        "description": "Test agent",
        "tool_ids": []
    }


class TestAgentCRUD:

    def test_create_agent(self, client, agent1, real_header):
        response = client.post(url="/agents",
                               json=agent1,
                               headers=real_header)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["name"] == agent1["name"]
        assert response_data["role"] == agent1["role"]
        assert response_data["description"] == agent1["description"]
        assert response_data["tenant_id"] == "tenant_a"

    def test_get_agents(self, client, agent1, agent2, real_header, fake_header):
        exists_agents = client.get(url="/agents",
                                   headers=real_header).json()
        agents = [agent1, agent2]
        for agent in agents:
            client.post(url="/agents",
                        json=agent,
                        headers=real_header)
        response = client.get(url="/agents",
                              headers=real_header)
        assert response.status_code == 200
        response_data = response.json()
        assert len(agents) + len(exists_agents) == len(response_data)

        response = client.get(url="/agents",
                              headers=fake_header)
        assert response.status_code == 401

    def test_get_agent_by_tool_name(self, client, agent1, agent2, tools, real_header):
        tool = client.post(url="/tools",
                           json=tools[0],
                           headers=real_header).json()

        exists_agent_by_tool = client.get(url=f"/agents?tool_name={tool['name']}",
                                          headers=real_header).json()
        agent1["tool_ids"] = [tool["id"]]
        client.post(url="/agents",
                    json=agent1,
                    headers=real_header)
        client.post(url="/agents",
                    json=agent2,
                    headers=real_header)
        agents_by_tool = client.get(url=f"/agents?tool_name={tool['name']}",
                                    headers=real_header)
        assert agents_by_tool.status_code == 200
        agents_by_tool = agents_by_tool.json()
        assert len(exists_agent_by_tool) + 1 == len(agents_by_tool)
        assert agents_by_tool[0]["name"] == agent1["name"]

    def test_create_agent_with_wrong_data(self, client, tools, real_header):
        response = client.post(url="/agents",
                               json=tools[0],
                               headers=real_header)
        assert response.status_code == 422

    def test_create_agent_with_invalid_tenant(self, client, agent1, fake_header):
        response = client.post(url="/agents",
                               json=agent1,
                               headers=fake_header)
        assert response.status_code == 401

        response = client.post(url="/agents",
                               json=agent1)
        assert response.status_code == 422

    def test_create_agent_with_invalid_tools(self, client, agent1, real_header):
        agent1["tool_ids"] = [1000]
        response = client.post(url="/agents",
                               json=agent1,
                               headers=real_header)
        assert response.status_code == 400

    def test_update_agent(self, client, agent1, real_header):
        agent = client.post(url="/agents",
                            json=agent1,
                            headers=real_header)
        response = client.put(url=f"/agents/{agent.json()['id']}",
                              json={"name": "New name"},
                              headers=real_header)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["name"] == "New name"
        assert response_data["role"] == agent1["role"]

    def test_run_agent_and_rate_limit_per_tenant(self, client, agent1, agent2, real_header):
        agent = client.post(url="/agents",
                            json=agent1,
                            headers={"X-API-Key": "tenant_c"}).json()

        other_agent = client.post(url="/agents",
                                  json=agent2,
                                  headers=real_header).json()

        for i in range(API_KEYS["tenant_c"]["request_limit"]):
            res_run_request = client.post(
                url=f"/agents/{agent['id']}/run",
                json={"task": f"Task {i}", "model": "gpt-4o"},
                headers={"X-API-Key": "tenant_c"})
            assert res_run_request.status_code == 200

        res_run_from_other_tenant = client.post(
            url=f"/agents/{other_agent['id']}/run",
            json={"task": f"Task from other tenant", "model": "gpt-4o"},
            headers=real_header)
        assert res_run_from_other_tenant.status_code == 200

        res_run_request = client.post(
            url=f"/agents/{agent['id']}/run",
            json={"task": "Rate limited task", "model": "gpt-4o"},
            headers={"X-API-Key": "tenant_c"})
        assert res_run_request.status_code == 429
        assert "Rate limit exceeded" in res_run_request.json().get("detail", "")

    def test_delete_agent(self, client, agent1, real_header):
        agent = client.post(url="/agents",
                            json=agent1,
                            headers=real_header).json()
        response = client.delete(url="/agents" + f"/{agent['id']}",
                                 headers=real_header)
        assert response.status_code == 200
        response = client.delete(url="/agents" + f"/{agent['id']}",
                                 headers=real_header)
        assert response.status_code == 404


class TestToolCRUD:

    def test_create_tool(self, client, tools, real_header):
        response = client.post(url="/tools",
                               json=tools[0],
                               headers=real_header)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["name"] == tools[0]["name"]
        assert response_data["description"] == tools[0]["description"]
        assert response_data["tenant_id"] == "tenant_a"

    def test_get_tools(self, client, tools, real_header, fake_header):
        exists_tools = client.get(url="/tools",
                                  headers=real_header).json()
        for tool in tools:
            client.post(url="/tools",
                        json=tool,
                        headers=real_header)
        response = client.get(url="/tools",
                              headers=real_header)
        assert response.status_code == 200
        response_json = response.json()
        assert len(tools) + len(exists_tools) == len(response_json)
        response = client.get(url="/tools",
                              headers=fake_header)
        assert response.status_code == 401

    def test_get_tool_by_id(self, client, tools, real_header):
        tool = client.post(url="/tools",
                           json=tools[0],
                           headers=real_header).json()
        response = client.get(url=f"/tools/{tool['id']}",
                              headers=real_header)
        assert response.status_code == 200
        response = response.json()
        assert response["name"] == tool["name"]

    def test_create_tool_with_wrong_tenant(self, client, tools, fake_header):
        response = client.post(url="/tools",
                               json=tools[0],
                               headers=fake_header)
        assert response.status_code == 401

    def test_update_tool(self, client, tools, real_header):
        tool = client.post(url="/tools",
                           json=tools[0],
                           headers=real_header).json()
        response = client.put(url=f"/tools/{tool['id']}",
                              json={"name": "New name"},
                              headers=real_header)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["name"] == "New name"
        assert response_data["description"] == tools[0]["description"]

    def test_delete_tool(self, client, tools, agent1, real_header):
        tool = client.post(url="/tools",
                           json=tools[0],
                           headers=real_header).json()
        agent1["tool_ids"] = [tool["id"]]
        agent = client.post(url="/agents",
                            json=agent1,
                            headers=real_header).json()
        response = client.delete(url="/tools" + f"/{tool['id']}",
                                 headers=real_header)
        assert response.status_code == 400

        client.delete(url=f"/agents/{agent['id']}",
                      headers=real_header)
        response = client.delete(url=f"/tools/{tool['id']}",
                                 headers=real_header)
        assert response.status_code == 200

        response = client.delete(url=f"/tools/{tool['id']}",
                                 headers=real_header)
        assert response.status_code == 404


class TestExecutions:

    def test_get_executions(self, client, agent1, real_header):
        agent = client.post(url="/agents",
                            json=agent1,
                            headers=real_header).json()
        exists_executions = client.get(url="/executions",
                                       headers=real_header).json()
        for i in range(5):
            client.post(
                url=f"/agents/{agent['id']}/run",
                json={"task": f"Task {i}", "model": "gpt-4o"},
                headers=real_header)
        response = client.get(url="/executions",
                              headers=real_header)
        assert response.status_code == 200
        assert len(exists_executions) + 5 == len(response.json())

        response = client.get(url="/executions" + "?page=1&page_size=2",
                              headers=real_header)
        assert len(response.json()) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
