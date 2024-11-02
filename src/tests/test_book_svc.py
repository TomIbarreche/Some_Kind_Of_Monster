# import json
# import pytest

# def test_create_book(client, create_verify_connect_content_creator_user, fake_create_book_data):
#     content_creator_token = create_verify_connect_content_creator_user
#     response = client.post("/api/v1/books", json=fake_create_book_data,headers={"Authorization":f"Bearer {content_creator_token}"})
#     assert response.status_code == 201
#     assert response.json()["id"] == 1
#     assert response.json()["creator_id"] == 2
#     assert response.json()["users"][0]["id"] == 2
#     assert response.json()["users"][0]["email"] == "content@content.content"

# def test_create_book_without_role(client, create_verify_connect_standard_user, fake_create_book_data):
#     user_token = create_verify_connect_standard_user
#     response = client.post("/api/v1/books", json=fake_create_book_data,headers={"Authorization":f"Bearer {user_token}"})
#     assert response.status_code == 403
#     assert response.json()["initial_details"]["error_code"] == "insufficient_permission"
#     assert response.json()["info"]["error"] == "Roles ['admin', 'content_creator'] are required"

# @pytest.mark.parametrize(
#     "search, limit, offset, response_len, book_title",
#     [
#         ["",2,0,2, "Fake v1"],
#         ["",1,0,1, "Fake v1"],
#         ["", 2,1,1, "Coin"],
#         ["Coin",2,0,1, "Coin"]
#     ]
# )
# def test_get_all_books(client, create_books, search, limit, offset, response_len, book_title):
#     content_creator_token = create_books
#     response = client.get(f"/api/v1/books?search={search}&limit={limit}&offset={offset}",headers={"Authorization":f"Bearer {content_creator_token}"})
#     assert response.status_code == 200
#     assert len(response.json()) == response_len
#     assert response.json()[0]["name"] == book_title

# @pytest.mark.parametrize(
#     "limit, offset, err_status_code, err_msg",
#     [
#         [0,0, 422,"Input should be greater than 0"],
#         [1,-1,422,"Input should be greater than -1" ]
#     ]
# )
# def test_get_all_books_with_query_errors(client, limit, offset, err_status_code, err_msg, create_books):
#     content_creator_token = create_books
#     response = client.get(f"/api/v1/books?limit={limit}&offset={offset}",headers={"Authorization":f"Bearer {content_creator_token}"})
#     assert response.status_code == err_status_code
#     assert response.json()["detail"][0]["msg"] == err_msg

# def test_get_all_books_without_right_role(client,create_books, create_verify_connect_standard_user):
#     create_books
#     user_token = create_verify_connect_standard_user
#     response = client.get("/api/v1/books",headers={"Authorization":f"Bearer {user_token}"})
#     assert response.status_code == 403
#     assert response.json()["initial_details"]["error_code"] == "insufficient_permission"
#     assert response.json()["info"]["error"] == "Roles ['admin', 'content_creator'] are required"

# def test_get_book_by_id(client, create_book):
#     content_creator_token = create_book
#     response = client.get("/api/v1/books/1", headers={"Authorization": f"Bearer {content_creator_token}"})
#     assert response.status_code == 200
#     assert response.json()["id"] == 1
#     assert response.json()["creator_id"] == 2

# @pytest.mark.parametrize(
#     "book_id, token, err_status_code, err_msg, err_code",
#     [
#         [1, "expired_token", 401, "Signature has expired", "token_decode_fail"],
#         [0,"create_verify_connect_standard_user", 404, "Book with this Id not found", "book_not_found"]
#     ]
# )
# def test_get_book_by_id_with_error(client, create_book, book_id, token, err_status_code, err_msg, err_code, request):
#     create_book
#     user_token = request.getfixturevalue(token)
#     response = client.get(f"/api/v1/books/{book_id}", headers={"Authorization": f"Bearer {user_token}"})
#     assert response.status_code == err_status_code
#     assert response.json()["initial_details"]["error_code"] == err_code
#     assert response.json()["info"]["error"] == err_msg
 
# def test_update_book(client, create_book, fake_create_book_data_2):
#     content_creator_token = create_book
#     response = client.patch("/api/v1/books/1", json=fake_create_book_data_2, headers={"Authorization": f"Bearer {content_creator_token}"})
#     assert response.status_code == 200
#     assert response.json()["id"] == 1
#     assert response.json()["name"] == fake_create_book_data_2["name"]

# @pytest.mark.parametrize(
#         "book_id, token, err_status_code, err_msg, err_code",
#         [
#             [1, "expired_token", 401, "Signature has expired", "token_decode_fail"],
#             [1, "create_verify_connect_standard_user",403, "Roles ['admin', 'content_creator'] are required","insufficient_permission"],
#             [1, "create_verify_connect_content_creator_user_2", 403, "You are not authorized to update a book you dont created", "update_not_allowed"],
#             [0, "create_verify_connect_content_creator_user", 404, "Book with this Id not found", "book_not_found"]
#         ]
# )
# def test_update_book_with_errors(client, book_id, token, err_status_code, err_msg, err_code, request, fake_create_book_data_2, create_book):
#     access_token = request.getfixturevalue(token)
#     response = client.patch(f"/api/v1/books/{book_id}", json=fake_create_book_data_2, headers={"Authorization": f"Bearer {access_token}"})
#     assert response.status_code == err_status_code
#     assert response.json()["initial_details"]["error_code"] == err_code
#     assert response.json()["info"]["error"] == err_msg

# def test_delete_book(client, create_book, connect_admin):
#     create_book
#     admin_token = connect_admin
#     response = client.delete("/api/v1/books/1", headers={"Authorization": f"Bearer {admin_token}"})
#     assert response.status_code == 204

# @pytest.mark.parametrize(
#     "book_id, token, err_status_code, err_msg, err_code",
#     [
#         [1, "create_book", 403, "Roles ['admin'] are required","insufficient_permission"],
#         [0, "connect_admin", 404,"Book with this Id not found", "book_not_found"]
#     ]
# )
# def test_delete_with_errors(client, err_status_code, err_msg, err_code, book_id, token, request):
#     token = request.getfixturevalue(token)
#     response = client.delete(f"/api/v1/books/{book_id}", headers={"Authorization":f"Bearer {token}"})
#     assert response.status_code == err_status_code
#     assert response.json()["initial_details"]["error_code"] == err_code
#     assert response.json()["info"]["error"]== err_msg