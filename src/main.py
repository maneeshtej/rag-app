from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_core.messages import HumanMessage, AIMessage
from src.services.user_service import create_user, user_login
from src.bootstrap.bootstrap import create_app, create_vector_store
from src.schema.schema import schema, system_user, schema
from src.schema.setup_schema import schema_to_documents

def create_loader(path: str):
    if path.endswith(".txt"):
        return TextLoader(path)
    elif path.endswith(".pdf"):
        return PyPDFLoader(path)
    elif path.endswith(".docx"):
        return Docx2txtLoader(path)
    else:
        raise ValueError("Unsupported file type")

def main():
    print("_" * 100)
    print("Simple Naive RAG CLI")
    print("Commands:")
    print("  create        -> create a user")
    print("  login         -> login as a user")
    print("  query         -> ask a question")
    print("  add           -> ingest a text file")
    print("  list          -> list all the uploaded files")
    print("  delete        -> delete a file with source")
    print("  exit          -> quit")
    print("  update schema -> ingest SQL schema into vector store")

    print("_" * 100)

    app = create_app()

    current_user = system_user

    while True:
        cmd = input(">> ").strip()

        if cmd.lower() in {"exit", "quit"}:
            break

        elif cmd.lower() == "create":
            username = input("username: ").strip()
            role = input("role (admin/user/etc): ").strip()
            level = int(input("access level (1=highest): ").strip())

            current_user = create_user(
                username=username,
                role=role,
                access_level=level,
            )

            print("User created & set as current:")
            print(current_user)

        elif cmd.lower() == "login":
            username = input("username: ").strip()
            user = user_login(username)
            if user == None:
                print(f"User {username} does not exist.")
                continue

            current_user = user

        elif cmd.lower() == "query":
            if current_user is None:
                print("No user set. Run `login` or `create` first.\n")
                continue

            print("Entering chat mode. Type `quit` or `exit` to leave.\n")

            chat_history = []  # List[HumanMessage | AIMessage]

            while True:
                query = input("you> ").strip()

                if query.lower() in {"quit", "exit"}:
                    print("Exiting chat mode.\n")
                    break

                test = True

                answer = app.inference(
                    query=query,
                    user=current_user,
                    chat_history=chat_history,
                    test=test
                )

                print(f"assistant> {answer}\n")
                if not test:
                    chat_history.append(HumanMessage(content=query))
                    chat_history.append(AIMessage(content=answer))

                    if len(chat_history) > 10:  
                        chat_history = chat_history[-10:]


        elif cmd.lower() == "list":
                    if current_user is None:
                        print("No user set. Run `create` first.\n")
                        continue

                    files = app.vector_retriever.list_files(current_user)
                    print(files)        

        elif cmd.lower() == "add":
            if current_user is None:
                print("No user set. Run `create` first.\n")
                continue

            ingest_type = input("ingest type (vector/sql): ").strip().lower()

            if ingest_type == "vector":
                filepath = input("filepath: ").strip()
                loader = create_loader(path=filepath)

                result = app.ingest_vector(
                    loader=loader,
                    user=current_user
                )

                print("Vector ingestion completed.")
                print(result)

            elif ingest_type == "sql":
                image_path = input("image path: ").strip()

                result = app.ingest_sql(
                    path=image_path,
                    user=current_user
                )

                print("SQL ingestion completed.")
                print(result)

            else:
                print("Invalid ingest type. Choose `vector` or `sql`.")


        elif cmd.lower() == "delete":
            if current_user is None:
                print("No user set. Run `create` first.\n")
                continue

            source = input("source: ")
            if not source or source == "":
                print("Try again")
                continue

            output = app.vector_retriever.delete_file(source)
            print(output)

        elif cmd.lower() == "update schema":

            docs = schema_to_documents(schema=schema, user=system_user)
            result = app.ingest_schema(docs=docs)

            print("Schema ingestion completed.")
            print(result)

                

        else:
            print("Try again")

        


if __name__ == "__main__":
    main()
