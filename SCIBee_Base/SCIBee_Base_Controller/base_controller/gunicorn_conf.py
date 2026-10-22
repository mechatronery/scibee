def post_worker_init(worker):
    from base_controller import init_time, init_logger

    init_time()
    init_logger()
