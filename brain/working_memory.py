class WorkingMemory:

    def __init__(self):

        self.messages = []

    def add(
        self,
        role,
        content
    ):

        self.messages.append({

            "role": role,

            "content": content

        })

        self.messages = self.messages[-20:]

    def recent(self):

        return self.messages

    def clear(self):

        self.messages.clear()

    def debug(self):

        print()

        print("===== Working Memory =====")

        if not self.messages:

            print("Empty")

        for item in self.messages:

            print(

                f"{item['role']}: {item['content']}"

            )

        print("==========================")

        print()


working_memory = WorkingMemory()