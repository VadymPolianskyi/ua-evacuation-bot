import logging

file_name = 'Результат-{}-{}.txt'


def create_text_file(text: str, service_type: str, user_id: int):
    logging.info(f"Create file response for User({user_id})")
    fn = file_name.format(service_type, user_id)
    with open(fn, 'w') as f:
        f.write(text)
    return open(fn, 'rb')


def close(f):
    f.close()
    logging.info("Closed file")
