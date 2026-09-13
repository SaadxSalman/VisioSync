import unittest

from fastapi.testclient import TestClient

from backend.main import app


class ApiContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_contract(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertIn("documents", response.json())

    def test_query_contract(self) -> None:
        response = self.client.post("/query", json={"query": "supply fan alarm", "top_k": 2})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("answer", body)
        self.assertIn("hits", body)
        self.assertIn("latency_ms", body)

    def test_rejects_non_pdf_uploads(self) -> None:
        response = self.client.post("/documents", files={"file": ("notes.txt", b"not a pdf", "text/plain")})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
