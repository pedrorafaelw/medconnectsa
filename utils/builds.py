
def repeticao():
    while True:
        try:
            escolha = int(input('\n1- Tentar novamente\n2- Sair\n'))
            if escolha == 1:
                return True
            elif escolha == 2:
                return False
            else:
                print('Resposta inválida, tente novamente...')
                continue
        except ValueError:
            print('Resposta inválida, tente novamente...')
            continue
    
    