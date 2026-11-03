class NodoArbol:

  def __init__(self, valor):
    self.valor = valor
    self.izquierdo = None
    self.derecho = None


raiz = NodoArbol("Raíz")
raiz.izquierdo = NodoArbol("Hijo Izquierdo")
raiz.derecho = NodoArbol("Hijo Derecho")

print("Nodo Raíz:", raiz.valor)
print("Hijo Izquierdo:", raiz.izquierdo.valor)
print("Hijo Derecho:", raiz.derecho.valor)