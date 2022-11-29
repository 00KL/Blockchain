import datetime
import json
import hashlib
import time
from flask import Flask, jsonify

max_nonce = 2 ** 32  # 4 billion
nbits = 486604799


# Blockchain simples em Python
class Blockchain:
    # Construtor da classe, chamava a função de criação do bloco genesis
    # e armazena bloco genesis
    def __init__(self):
        self.chain = []
        self.create_blockchain( previous_hash='0')
        self.current_transactions = []

    # Cria um novo bloco
    def create_blockchain(self, previous_hash):
        # Estrutura do bloco
        # index: índice do bloco, tamanho da blockchain até este bloco
        # timestamp: data e hora do bloco
        # proof: prova do bloco
        # previous_hash: hash do bloco anterior
        # Current_transactions: transações do bloco atual
        # cuurent_transactions_hash: hash das transações do bloco atual
        block = {
            'nbits': nbits,
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'nonce': '',
            'proof': '',
            'previous_hash': previous_hash,
            'transactions': [],
            'transactions_hash': 0
        }

        self.chain.append(block)
        return block

    # Pega o último bloco da blockchain
    def get_previous_block(self):
        last_block = self.chain[-1]
        return last_block

    def calculate_target(self, bits):
        exp = bits >> 24
        mant = bits & 0xffffff
        target_hexstr = '%064x' % (mant * (1 << (8*(exp - 3))))
        # target_str = target_hexstr.decode('hex')
        return int(target_hexstr, 16)

    # Prova de trabalho, busca gastar o porder de processamento da máquina
    # afim de encontrar uma hash que satisfaça o requisito de 4 zeros.
    def proof_of_work(self, header, difficulty_bits):
        # calculate the difficulty target
        target = self.calculate_target(difficulty_bits)
        check_proof = False
        nonce = 0

        while check_proof == False:
            str_encoded = (str(header) + str(nonce)).encode()
            hash_result = hashlib.sha256(str_encoded).hexdigest()
            hash_result = hashlib.sha256(hash_result.encode()).hexdigest()

            # print("Nonce: ", nonce, "Hash: ", hash_result)
            print(int(hash_result, 16), " < ", target)

            # check if this is a valid result, below the target
            if int(hash_result, 16) < target:
                check_proof = True 
            else:
                nonce += 1

        return (hash_result, nonce)

    # Gera um hash do bloco
    def hash(self, block):
        # Converte o bloco para json então codifica a mensagem em utf-8
        encoded_block = json.dumps(block, sort_keys=True).encode()
        # Gera o hash do bloco e retorna o hash em hexadecimal
        return hashlib.sha256(encoded_block).hexdigest()

    def save_transaction_in_block(self, block):
        # Pega o hash das transações e atribui ao bloco atualmente sendo minerado
        block['transactions'] = self.current_transactions
        # Limpa as transações da lista de transações
        self.current_transactions = []
        # Gera o hash das transações
        block.transactions_hash = self.hash(block.transactions)

    # Verifica se a blockchain é válida
    def is_chain_valid(self, chain):
        # Pega o primeiro bloco da blockchain e usa como bloco anterior
        previous_block = chain[0]
        # Declara o índice para percorrer a blockchain
        block_index = 1
        while block_index < len(chain):
            # Pega o bloco atual
            block = chain[block_index]
            # Verifica se o hash do bloco anterior é igual ao hash do bloco atual
            # se não for a blockchain é inválida e retorna falso
            if block["previous_hash"] != self.hash(previous_block):
                return False
            
            # Atualiza o bloco anterior para o bloco atual
            previous_block = block
            # Incrementa o índice para percorrer a blockchain
            block_index += 1
        # Se a blockchain não foi invalidada até este ponto retorna verdadeiro
        return True


app = Flask(__name__)

blockchain = Blockchain()


@app.route('/mine_block', methods=['GET'])
# Função para minerar um bloco
def mine_block():
    # Reune os dados necessários para criar um novo bloco

    # Pegando o hash do último bloco
    # Pega último bloco
    previous_block = blockchain.get_previous_block()
    # Pega o hash do último bloco
    previous_hash = blockchain.hash(previous_block)

    # Limpa as transações da lista de transações
    blockchain.current_transactions = []

    # Cria um novo bloco
    block = blockchain.create_blockchain(previous_hash)

    # Gera uma string com as informações que compõem o bloco
    header = block['timestamp'] + block['previous_hash'] + \
        str(block['transactions_hash'])
    # Pega as transações atualmente na lista de transações e hash gerada por elas
    # Salva as transações no bloco
    block['transactions'] = blockchain.current_transactions
    block['transactions_hash'] = blockchain.hash(
        blockchain.current_transactions)

    # Gera um

    # Gera nonce
    # Gera uma nova prova
    (block['proof'], block['nonce']) = blockchain.proof_of_work(header, block['nbits'])

    # Gera a resposta em json
    response = {'message': 'Block mined!',
                'nbits': block['nbits'],
                'index': block['index'],
                'timestamp': block['timestamp'],
                'nonce': block['nonce'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions'],
                'transactions_hash': block['transactions_hash']}
    # Retorna a resposta em json
    return jsonify(response), 200

# Função para pegar a blockchain


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


@app.route('/new_transaction/<transaction>', methods=['post'])
def new_transactions(transaction):
    # Adiciona uma nova transação na lista de transações
    blockchain.current_transactions.append(str(transaction))
    return jsonify({'message': 'Transaction added to the block!'}), 201


@app.route('/get_transactions', methods=['GET'])
def get_transactions():
    response = {'transactions': list(blockchain.current_transactions)}
    return jsonify(response), 200


app.run(host='0.0.0.0', port=5000)
