from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_core.messages import HumanMessage, AIMessage
from src.database.db import get_connection
from src.schema.generate_rules import generate_rules
from src.services.scrape_service import parse_faculty_from_url
from src.services.user_service import create_user, user_login
from src.bootstrap.bootstrap import create_app
from src.schema.schema import schema, system_user
from src.schema.realisation_rules import realisation_rules
from src.bootstrap.bootstrap import conn
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
    print("  update schema -> ingest SQL schema and rules into store")

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

                test = False

                answer = app.inference(
                    query=query,
                    user=current_user,
                    chat_history=chat_history,
                    test=test
                )

                print(f"\n\n\n\nassistant> {answer}\n")
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

            ingest_type = input("ingest type (vector/sql/faculty): ").strip().lower()

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

            elif ingest_type == "faculty":
                profiles = parse_faculty_from_url("https://nitte.edu.in/nmit/btech-computer-science-engineering.php")
                try:
                    result = app.ingest_faculty_profiles(
                        profiles=profiles,
                        dept_name="Computer Science and Engineering",
                        user=system_user,
                        truncate=True
                    )
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    print(e)
                    

                print(result)
                print("ingestion completed")

            else:
                print("Invalid ingest type. Choose `vector` or `sql` or `faculty`.")


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
            try:
                result = app.ingest_schema(
                    realisation_rules=realisation_rules,
                    schema=schema,
                    generate_rules=generate_rules,
                    truncate=True
                )
                # print(result)
                print("Schema ingestion completed.")
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(e)

        else:
            print("Try again")

if __name__ == "__main__":
    main()
