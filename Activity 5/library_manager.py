import pymongo
from bson.objectid import ObjectId
from datetime import datetime
import pprint

# --- 1. CONFIGURAÇÃO DO BANCO DE DADOS ---
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["library_db"]
books_col = db["books"]
authors_col = db["authors"]

# Garante que o ISBN seja único (cria um índice no banco)
books_col.create_index("isbn", unique=True)

# --- 2. FUNÇÕES AUXILIARES ---
def get_date_input(prompt):
    while True:
        date_str = input(prompt + " (YYYY-MM-DD): ")
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("Formato inválido. Use AAAA-MM-DD.")

# --- 3. CRUD AUTORES ---

def create_author():
    print("\n--- Adicionar Autor ---")
    name = input("Nome: ")
    nationality = input("Nacionalidade: ")
    birthdate = get_date_input("Data de Nascimento")
    
    if not name or not nationality:
        print("Erro: Nome e Nacionalidade são obrigatórios.")
        return

    author_doc = {
        "name": name,
        "birthdate": birthdate,
        "nationality": nationality,
        "books": [] # Array de referências para livros
    }
    
    result = authors_col.insert_one(author_doc)
    print(f"Autor criado com sucesso! ID: {result.inserted_id}")

def list_authors(page=1, page_size=5): # Com Paginação (Bônus)
    skips = page_size * (page - 1)
    authors = list(authors_col.find().skip(skips).limit(page_size))
    
    if not authors:
        print("Nenhum autor encontrado nesta página.")
        return

    for author in authors:
        print(f"ID: {author['_id']} | Nome: {author['name']} | Livros: {len(author['books'])}")

def delete_author():
    author_id = input("ID do Autor para deletar: ")
    try:
        obj_id = ObjectId(author_id)
    except:
        print("ID inválido.")
        return

    # Requisito: Cascade Delete (Apagar autor apaga seus livros)
    # Primeiro, deletamos os livros associados a este autor
    delete_books_result = books_col.delete_many({"author_id": obj_id})
    
    # Depois, deletamos o autor
    result = authors_col.delete_one({"_id": obj_id})
    
    if result.deleted_count > 0:
        print(f"Autor deletado. {delete_books_result.deleted_count} livros associados também foram removidos.")
    else:
        print("Autor não encontrado.")

# --- 4. CRUD LIVROS ---

def create_book():
    print("\n--- Adicionar Livro ---")
    # Listar autores para pegar o ID
    print("Autores disponíveis:")
    list_authors(page=1, page_size=20)
    
    author_id_input = input("ID do Autor deste livro: ")
    try:
        author_oid = ObjectId(author_id_input)
        author = authors_col.find_one({"_id": author_oid})
        if not author:
            print("Autor não encontrado.")
            return
    except:
        print("ID de autor inválido.")
        return

    title = input("Título: ")
    isbn = input("ISBN: ")
    genre = input("Gênero: ")
    try:
        year = int(input("Ano de Publicação: "))
    except:
        print("Ano deve ser um número.")
        return

    # Validação simples
    if not title or not isbn:
        print("Título e ISBN são obrigatórios.")
        return

    book_doc = {
        "title": title,
        "author_name": author['name'], # Desnormalização (guardando string)
        "author_id": author_oid,       # Referência
        "published_year": year,
        "genre": genre,
        "isbn": isbn
    }

    try:
        result = books_col.insert_one(book_doc)
        new_book_id = result.inserted_id
        
        # Atualizar o documento do Autor para incluir a referência do livro
        authors_col.update_one(
            {"_id": author_oid},
            {"$push": {"books": new_book_id}}
        )
        print(f"Livro criado! ID: {new_book_id}")
        
    except pymongo.errors.DuplicateKeyError:
        print("Erro: Já existe um livro com esse ISBN.")

def search_books(): # Bônus: Busca
    query = input("Buscar livros por título ou nome do autor: ")
    # Regex para busca insensível a maiúsculas/minúsculas
    regex_query = {"$regex": query, "$options": "i"}
    
    results = books_col.find({
        "$or": [
            {"title": regex_query},
            {"author_name": regex_query}
        ]
    })
    
    found = False
    for book in results:
        found = True
        pprint.pprint(book)
    
    if not found:
        print("Nenhum livro encontrado.")

def update_book():
    book_id = input("ID do Livro para atualizar: ")
    try:
        obj_id = ObjectId(book_id)
    except:
        print("ID inválido.")
        return

    new_title = input("Novo título (deixe em branco para manter): ")
    update_data = {}
    if new_title:
        update_data["title"] = new_title

    if update_data:
        books_col.update_one({"_id": obj_id}, {"$set": update_data})
        print("Livro atualizado.")
    else:
        print("Nenhuma alteração feita.")

def delete_book():
    book_id = input("ID do Livro para deletar: ")
    try:
        obj_id = ObjectId(book_id)
    except:
        print("ID inválido.")
        return

    # Primeiro, descobrimos quem é o autor para remover a referência do array dele
    book = books_col.find_one({"_id": obj_id})
    if book:
        # Remove do array de livros do autor
        authors_col.update_one(
            {"_id": book['author_id']},
            {"$pull": {"books": obj_id}}
        )
        # Remove o livro
        books_col.delete_one({"_id": obj_id})
        print("Livro removido e lista do autor atualizada.")
    else:
        print("Livro não encontrado.")

# --- 5. MENU PRINCIPAL (CLI) ---

def main():
    while True:
        print("\n=== GERENCIADOR DE BIBLIOTECA ===")
        print("1. Adicionar Autor")
        print("2. Listar Autores")
        print("3. Remover Autor (Cuidado: Remove livros associados!)")
        print("4. Adicionar Livro")
        print("5. Buscar Livros (Título/Autor)")
        print("6. Atualizar Livro")
        print("7. Remover Livro")
        print("0. Sair")
        
        choice = input("Opção: ")
        
        if choice == '1': create_author()
        elif choice == '2': list_authors()
        elif choice == '3': delete_author()
        elif choice == '4': create_book()
        elif choice == '5': search_books()
        elif choice == '6': update_book()
        elif choice == '7': delete_book()
        elif choice == '0': break
        else: print("Opção inválida.")

if __name__ == "__main__":
    main()