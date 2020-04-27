def search_id_template(client_id: str):
    return {"query": {"match": {"client_id": {"query": client_id, "operator": "and"}}}}


def search_email_template(email: str):
    return {"query": {"match": {"email": {"query": email, "operator": "and"}}}}


def search_contact_number_template(contact_number: str):
    return {"query": {"match": {"contact_number": {"query": contact_number, "operator": "and"}}}}


def search_email_and_contact_number_template(email: str, contact_number: str):
    return {"query": {"bool": {"must": [{"match": {"contact_number": {"query": contact_number, "operator": "and"}}},
                                        {"match": {"email": {"query": email, "operator": "and"}}}
                                        ]}}}


def search_email_or_contact_number_template(email: str, contact_number: str):
    return {
        "query": {"bool": {"should": [{"term": {"email": email}}, {"term": {"contact_number": contact_number}}]}}}


def search_name_template(name: str):
    return {"query": {"match": {"client_name": {"query": name, "operator": "and"}}}}
