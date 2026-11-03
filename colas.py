from collections import deque

cola = deque(["Ana", "Carlos", "Beatriz"])
print("Cola inicial:", cola)

cola.append("David")
print("Cola con nuevo cliente:", cola)

atendido = cola.popleft()
print(f"Atendido a: {atendido}")
print("Cola restante:", cola)