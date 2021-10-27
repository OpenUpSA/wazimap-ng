import pytest

from django_q.tasks import async_task
from tests.general.factories import TaskFactory


@pytest.mark.focus
@pytest.mark.django_db
def test_task_status(tp, tp_api):
    reversed_url = tp.reverse(
        "task_status",
        task_id="1234",
    )
    response = tp_api.client.get(reversed_url, format="json")

    assert response.status_code == 200


def short_task():
    return 1


@pytest.mark.django_db
def test_task_status_success(tp, tp_api):
    task_id = async_task(short_task)

    reversed_url = tp.reverse(
        "task_status",
        task_id=task_id,
    )
    response = tp_api.client.get(reversed_url, format="json")
    js = response.json()

    assert response.status_code == 200
    assert js["status"] == "success"


@pytest.mark.django_db
def test_task_status_running(tp, tp_api):
    reversed_url = tp.reverse(
        "task_status",
        task_id="1234",
    )
    response = tp_api.client.get(reversed_url, format="json")
    js = response.json()

    assert response.status_code == 200
    assert js["status"] == "running"


@pytest.mark.django_db
def test_task_status_failure(tp, tp_api):
    task = TaskFactory(success=False)

    reversed_url = tp.reverse(
        "task_status",
        task_id=task.name,
    )
    response = tp_api.client.get(reversed_url, format="json")
    js = response.json()

    assert response.status_code == 200
    assert js["status"] == "error"
