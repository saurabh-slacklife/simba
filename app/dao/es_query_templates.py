#######################

# Client Templates

def search_client_by_id_template(client_id: str):
    return {"query": {"match": {"client_id": {"query": client_id, "operator": "and"}}}}


def search_client_by_email_template(email: str):
    return {"query": {"match": {"email": {"query": email, "operator": "and"}}}}


def search_client_by_contact_number_template(contact_number: str):
    return {"query": {"match": {"contact_number": {"query": contact_number, "operator": "and"}}}}


def search_client_by_email_and_contact_number_template(email: str, contact_number: str):
    return {"query": {"bool": {"must": [{"match": {"contact_number": {"query": contact_number, "operator": "and"}}},
                                        {"match": {"email": {"query": email, "operator": "and"}}}
                                        ]}}}


def search_client_by_email_or_contact_number_template(email: str, contact_number: str):
    return {
        "query": {"bool": {"should": [{"term": {"email": email}}, {"term": {"contact_number": contact_number}}]}}}


def search_client_by_name_template(name: str):
    return {"query": {"match": {"client_name": {"query": name, "operator": "and"}}}}

#####################################

# User templates

def search_user_by_id_template(user_id: str):
    return {"query": {"match": {"user_id": {"query": user_id, "operator": "and"}}}}
