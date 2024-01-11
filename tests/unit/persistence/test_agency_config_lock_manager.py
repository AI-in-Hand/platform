import threading

from nalgonda.persistence.agency_config_lock_manager import AgencyConfigLockManager


def test_lock_uniqueness():
    agency_id1 = "agency1"
    agency_id2 = "agency2"

    lock1 = AgencyConfigLockManager.get_lock(agency_id1)
    lock2 = AgencyConfigLockManager.get_lock(agency_id2)

    assert lock1 is not lock2, "Different agencies should have different locks"


def test_lock_for_same_agency():
    agency_id = "agency1"

    lock1 = AgencyConfigLockManager.get_lock(agency_id)
    lock2 = AgencyConfigLockManager.get_lock(agency_id)

    assert lock1 is lock2, "The same agency should return the same lock instance"


def test_lock_concurrency_handling():
    agency_id = "agency1"
    lock = AgencyConfigLockManager.get_lock(agency_id)

    # Define a shared resource
    shared_resource = []

    def task():
        with lock:
            shared_resource.append(1)

    # Run tasks in parallel to simulate concurrent access
    threads = [threading.Thread(target=task) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(shared_resource) == 10, "Concurrency issue: shared resource was accessed simultaneously"
