"""
Heartbeat worker that sends heartbeats periodically.
"""

import os
import pathlib
import time

from pymavlink import mavutil

from utilities.workers import worker_controller
from . import heartbeat_sender
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
HEARTBEAT_PERIOD = 1.0


def heartbeat_sender_worker(
    connection: mavutil.mavfile,
    controller: worker_controller.WorkerController,
    local_logger: logger.Logger | None = None,
) -> None:
    """
    Worker process.

    connection: connection between drone and worker
    controller: controls worker process
    local_logger: logs info, errors, etc. if they occur
    """
    # =============================================================================================
    #                          ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
    # =============================================================================================

    # Instantiate logger
    worker_name = pathlib.Path(__file__).stem
    process_id = os.getpid()
    result, local_logger = logger.Logger.create(f"{worker_name}_{process_id}", True)
    if not result:
        print("ERROR: Worker failed to create logger")
        return

    # Get Pylance to stop complaining
    assert local_logger is not None

    local_logger.info("Logger initialized", True)

    # =============================================================================================
    #                          ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
    # =============================================================================================
    creation_status, sender = heartbeat_sender.HeartbeatSender.create(connection, local_logger)
    if not creation_status:
        local_logger.error("Could not initialize Heartbeat Sender")
        return

    local_logger.info("Heartbeat sender initialized")

    while not controller.is_exit_requested():
        controller.check_pause()

        start_time = time.time()
        success, _ = sender.run()
        if not success:
            local_logger.warning("Failed to send Heartbeat")

        sleep_time = HEARTBEAT_PERIOD - (time.time() - start_time)
        if sleep_time > 0:
            time.sleep(sleep_time)


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
