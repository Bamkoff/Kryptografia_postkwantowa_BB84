from qiskit import QuantumCircuit, BasicAer, transpile, assemble, execute
import numpy as np
from qiskit.visualization import plot_histogram


# Checks if two list have same values on corresponding indexes
def lists_equal(l1, l2):
    if len(l1) != len(l2):
        return False
    for index, value in enumerate(l1):
        if value != l2[index]:
            return False
    return True


# Generates random string of bits of length n
def generate_string(n: int):
    if n > 0:
        bit_list = []
        for i in range(n):
            bit_list.append(np.random.randint(0, 2))
        return bit_list
    return []


# Changes values in Quantum Circuit to opposite if on corresponding index in base_list is value 1
def prepare_quantum_circuit(bit_list, quantum_circuit, debug):
    for index, bit in enumerate(bit_list):
        if bit == 1:
            quantum_circuit.x(index)
    quantum_circuit.barrier()
    if debug:
        print('Preparing Quantum Circuit:')
        print(quantum_circuit)


# Work with gate H on inputs in Quantum Circuit which have 1 on responding index in base_list
def get_bit_representation(base_list, quantum_circuit, debug):
    for index, bit in enumerate(base_list):
        if bit == 1:
            quantum_circuit.h(index)
    quantum_circuit.barrier()
    if debug:
        print('Working on Quantum Circuit with gate H:')
        print(quantum_circuit)


# Measure cubits in Quantum Circuit
def get_measurements(length, quantum_circuit, debug):
    for i in range(length):
        quantum_circuit.measure(i, i)
    if debug:
        print('Measuring cubits in Quantum Circuit')
        print(quantum_circuit)

    aer_sim = BasicAer.get_backend('qasm_simulator')
    job = execute(quantum_circuit, backend=aer_sim, shots=1).result()
    return job


# Simulation of bb84 protocol
# key length of Alice's private key which is generated at the beginning of this function
# debug value means if additional information should be printed out
# eve value means if the simulation should contain eavesdropping
def bb84_protocol_simulation(key_length=10, debug=False, eve=False):
    # generation of random key
    alice_key = generate_string(key_length)
    if debug:
        print(f'generated key: {alice_key}')

    # main part of the protocol

    # Alice's preparations
    qc = QuantumCircuit(key_length, key_length)
    alice_base_list = generate_string(key_length)

    # Alice sets up initial values of inputs in Quantum Circuit
    prepare_quantum_circuit(alice_key, qc, debug)

    if debug:
        print(f'Alice\'s randomly chosen bases: {alice_base_list}')

    # Alice sends key encoded in Quantum Circuit
    get_bit_representation(alice_base_list, qc, debug)

    # Eve's eavesdropping
    if eve:
        eve_base_list = generate_string(key_length)
        if debug:
            print('---------------------------------------------------------------------------------------------------')
            print(f'Eve\'s randomly chosen bases: {eve_base_list}')

        # Eve uses her chosen gates on cubits in Quantum Circuit
        get_bit_representation(eve_base_list, qc, debug)

        # Eve takes measurements of cubits in Quantum Circuit
        get_measurements(key_length, qc, debug)

        qc.barrier()

    # Bob's preparations
    bob_base_list = generate_string(key_length)
    if debug:
        print('---------------------------------------------------------------------------------------------------')
        print(f'Bob\'s randomly chosen bases: {bob_base_list}')

    # Bob uses his chosen gates on cubits in Quantum Circuit
    get_bit_representation(bob_base_list, qc, debug)

    # Bob takes measurements of cubits in Quantum Circuit
    results = get_measurements(key_length, qc, debug)
    bob_key = list(results.get_counts())[0]
    bob_key_list = []
    for sign in bob_key:
        bob_key_list.append(int(sign))

    # measured key is in reverse so it needs adjusting
    bob_key_list.reverse()

    if debug:
        print(f'Measurement with highest probability: {bob_key_list}')
        print(f'Alice\'s randomly chosen bases: {alice_base_list}')
        print(f'Bob\'s randomly chosen bases: {bob_base_list}')

    # getting indexes with the same gates from Alice's and Bob's chosen bases.
    index_with_the_same_gate_list = []
    for index, gate in enumerate(alice_base_list):
        if gate == bob_base_list[index]:
            index_with_the_same_gate_list.append(index)

    if debug:
        print(f'List of indexes which have same bases chosen: {index_with_the_same_gate_list}')

    alice_substring_of_key = []
    bob_substring_of_key = []

    # creating substring d from indexes with the same gates
    for index in index_with_the_same_gate_list:
        alice_substring_of_key.append(alice_key[index])
        bob_substring_of_key.append(bob_key_list[index])

    if debug:
        print(f'Alice\'s substring: {alice_substring_of_key}')
        print(f'Bob\'s substring: {bob_substring_of_key}')

    if lists_equal(alice_substring_of_key, bob_substring_of_key):
        print(f'Agreed upon key: {alice_substring_of_key}')
    else:
        print('Eve was eavesdropping!')


if __name__ == '__main__':
    bb84_protocol_simulation(key_length=10, debug=True, eve=False)

