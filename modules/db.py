import random

from pocketbase import PocketBase


class DB:
    def __init__(self, url: str, email: str, password: str, collection: str):
        self.client = PocketBase(url)
        self.email = email
        self.password = password
        self.collection = collection

        self._login()
        
    def __len__(self):
        self._login()
        result = self.client.collection(self.collection).get_list(1, 1)
        return result.total_items

    def _login(self):
        if not self.client.auth_store.token:
            self.client.collection("_superusers").auth_with_password(
                self.email, self.password
            )

    def _safe_str(self, string: str):
        return string.strip().lower().replace(" ", "_")

    def get(self, content: str):
        self._login()
        content = self._safe_str(content)

        try:
            return self.client.collection(self.collection).get_first_list_item(
                f'content = "{content}"'
            )
        except Exception:
            return None

    def upsert(self, content: str, is_good: bool, type: int = -1):
        self._login()
        content = self._safe_str(content)

        existing = self.get(content)

        if existing:
            data = {
                "used": existing.used + (1 if is_good else -1),
                "type": type if type != -1 else existing.type,
            }
            return self.client.collection(self.collection).update(existing.id, data)
        else:
            data = {"content": content, "used": 1 if is_good else -1, "type": type}
            return self.client.collection(self.collection).create(data)
        
    def like(self, like_content: str):
        self._login()
        like_content = self._safe_str(like_content)
        
        try:
            return self.client.collection(self.collection).get_list(
                filter=f'content ~ "{like_content}"'
            ).items
        except Exception:
            return []

    def delete(self, content: str):
        self._login()
        content = self._safe_str(content)

        existing = self.get(content)
        if existing:
            return self.client.collection(self.collection).delete(existing.id)
        return False

    def sample(self, n: int):
        self._login()

        total = len(self)

        if total == 0:
            return []

        if n > total:
            return self.client.collection(self.collection).get_full_list()

        indices = random.sample(range(1, total + 1), n)
        ret = []
        for idx in indices:
            res = self.client.collection(self.collection).get_list(idx, 1)
            if res.items:
                ret.append(res.items[0])
        return ret

    def all(self, page: int, per_page: int):
        self._login()

        result = self.client.collection(self.collection).get_list(page, per_page)
        return result.items


if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    load_dotenv()
    POCKETBASE_URL = os.getenv("POCKETBASE_URL")
    POCKETBASE_ADMIN_EMAIL = os.getenv("POCKETBASE_ADMIN_EMAIL")
    POCKETBASE_ADMIN_PASSWORD = os.getenv("POCKETBASE_ADMIN_PASSWORD")
    POCKETBASE_COLLECTION = os.getenv("POCKETBASE_COLLECTION")

    db = DB(
        POCKETBASE_URL,
        POCKETBASE_ADMIN_EMAIL,
        POCKETBASE_ADMIN_PASSWORD,
        POCKETBASE_COLLECTION,
    )

    print(db.upsert("test content", True, 1))
    print(db.get("test content"))
    print(db.sample(1))
    print(db.delete("test content"))
    print(db.get("test content"))
