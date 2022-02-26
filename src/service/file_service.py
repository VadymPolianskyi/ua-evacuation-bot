file_name = 'Результат-{}-{}.txt'


def create_text_file(text: str, service_type: str, user_id: int):
    fn = file_name.format(service_type, user_id)
    with open(fn, 'w') as f:
        f.write(text)
    return open(fn, 'rb')


def close(f):
    f.close()
    print("Closed file")
