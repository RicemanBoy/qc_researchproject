from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.visualization import plot_histogram
import numpy as np
import matplotlib.pyplot as plt
import bitstring
from qiskit_aer import AerSimulator

from qiskit.circuit.library import QFT, CPhaseGate

from qiskit_aer.noise import (NoiseModel, QuantumError, ReadoutError,
    pauli_error, depolarizing_error, thermal_relaxation_error)


def step_1_circuit(qr: QuantumRegister, cr: ClassicalRegister, angle) -> QuantumCircuit:
    # qr is a quantum register with 2 qubits
    # cr is a classical register with 2 bits

    qc = QuantumCircuit(qr, cr)

    ########## your code goes here #######

    ##1 Initialization

    q0, q1 = qr
    # apply Hadamard on the auxiliary qubit
    qc.h(q0)
    # put the system qubit into the |1> state
    qc.x(q1)

    ##2 Apply control-U operator as many times as needed to get the least significant phase bit

    # we want to apply controlled-S 2^k times
    k = 0
    # calculate the angle of CPhase corresponding to 2^k applications of angle
    cphase_angle = angle * 2**k
    # apply the controlled phase gate
    qc.cp(cphase_angle, q0, q1)

    ##3 Measure the auxiliary qubit in x-basis into the first classical bit

    # apply Hadamard to change to the X basis
    qc.h(q0)
    # measure the auxiliary qubit into the first classical bit
    c0 = cr
    qc.measure(q0, c0)

    return qc

def iqpe(angle: float, steps: int, bits_list = []):
    if steps == 1:
        qr = QuantumRegister(2, "q")
        cr = ClassicalRegister(1, "c")
        return step_1_circuit(qr,cr,angle)                  #funktioniert!!!
    else:
        qr = QuantumRegister(2,"q")
        cr = ClassicalRegister(steps, "c")
        q0, q1 = qr

        list = []
        for i in range(97, 97+steps):                               #hier die Liste mit dem Classical Register
            list.append("{:c}".format(i))
        list = cr
        qc = QuantumCircuit(qr,cr)

        # apply Hadamard on the auxiliary qubit
        if not bits_list:                                                                                           #"Normaler" QPE-Circuit
            qc.h(q0)
            # put the system qubit into the |1> state
            qc.x(q1)
            ##2 Apply control-U operator as many times as needed to get the least significant phase bit
            # we want to apply controlled-S 2^k times
            k = steps-1
            # calculate the angle of CPhase corresponding to 2^k applications of angle
            cphase_angle = angle * 2**k
            # apply the controlled phase gate
            qc.cp(cphase_angle, q0, q1)
            ##3 Measure the auxiliary qubit in x-basis into the first classical bit
            # apply Hadamard to change to the X basis
            qc.h(q0)
            # measure the auxiliary qubit into the first classical bit                   
            qc.measure(q0, list[0])

            for i in range(1,steps):                                                                                                   
                qc.reset(q0)
                # apply Hadamard on the auxiiliary qubit
                qc.h(q0)

                ##2 Apply phase correction conditioned on the first classical bit

                for j in range(i):
                    with qc.if_test((list[j], 1)):
                        qc.p((-2*np.pi)/(2**(i-j+1)), q0)

                ##3 Apply control-U operator as many times as needed to get the next phase bit

                # we want to apply controlled-S 2^k times
                k = steps - i - 1
                # calculate the angle of CPhase corresponding to 2^k applications of controlled-S
                cphase_angle = angle * 2**k
                # apply the controlled phase gate
                qc.cp(cphase_angle, q0, q1)

                ##4 Measure the auxiliary qubit in x-basis into the second classical bit

                # apply Hadamard to change to the X basis
                qc.h(q0)
                # measure the auxiliary qubit into the first classical bit
                qc.measure(q0, list[i])
            
            return qc

        else:
            qc.x(q1)
            for j in range(len(bits_list)):
                qc.reset(q0)
                if bits_list[j] == "1":
                    qc.x(q0)
                    qc.measure(q0, list[j])


        qc.reset(q0)
        # apply Hadamard on the auxiiliary qubit
        qc.h(q0)

        ##2 Apply phase correction conditioned on the first classical bit

        for j in range(steps-1):
            if bits_list[j] == "1":
                qc.p((-2*np.pi)/(2**(steps-j)), q0)
            # with qc.if_test((list[j], 1)):
            #     qc.p((-2*np.pi)/(2**(i-j+1)), q0)

        # calculate the angle of CPhase corresponding to 2^k applications of controlled-S
        cphase_angle = angle
        # apply the controlled phase gate
        qc.cp(cphase_angle, q0, q1)

        ##4 Measure the auxiliary qubit in x-basis into the second classical bit

        # apply Hadamard to change to the X basis
        qc.h(q0)
        # measure the auxiliary qubit into the first classical bit
        qc.measure(q0, list[steps-1])
        
        return qc
#Funktioniert

def iqpe_improved_noisy(angle: float, noise_model, shots_per_it: list):                            #Länge der Liste + 1 gibt mir meine depth bzw. #Iterationen
    bits_list=[]
    if  len(shots_per_it) == 1:
        qr = QuantumRegister(2, "q")
        cr = ClassicalRegister(1, "c")
        return step_1_circuit(qr,cr,angle)                  #funktioniert!!!
    else:
        steps = len(shots_per_it) + 1
        qr = QuantumRegister(2,"q")
        cr = ClassicalRegister(1, "c")
        q0, q1 = qr

        list = []
        list.append("c0")
        list = cr

        qc = QuantumCircuit(qr,cr)

        # apply Hadamard on the auxiliary qubit                                             
        qc.h(q0)
        # put the system qubit into the |1> state
        qc.x(q1)
        ##2 Apply control-U operator as many times as needed to get the least significant phase bit
        # we want to apply controlled-S 2^k times
        k = steps-1
        # calculate the angle of CPhase corresponding to 2^k applications of angle
        cphase_angle = angle * 2**k
        # apply the controlled phase gate
        qc.cp(cphase_angle, q0, q1)
        ##3 Measure the auxiliary qubit in x-basis into the first classical bit
        # apply Hadamard to change to the X basis
        qc.h(q0)
        # measure the auxiliary qubit into the first classical bit                                    
        qc.measure(q0, list[0])                                                                                                     #Bis hier, nur step_1_circuit
        sim = AerSimulator()
        job = sim.run(qc, noise_model=noise_model,shots=shots_per_it[0])
        result = job.result()
        counts = result.get_counts()
        max_val = max(counts.values())
        max_keys = []
        for key in counts:
            if counts[key] == max_val:
                max_keys.append(key)
        chosen_one = max_keys[0]
        bits_list.append(chosen_one)

        for i in range(1,steps-1):                                                                                                    #Ab hier, gehts weiter über die for schleife
            qr = QuantumRegister(2,"q")
            cr = ClassicalRegister(1, "c")
            q0, q1 = qr
            list = []
            list.append("c0")
            list = cr
            qc = QuantumCircuit(qr,cr)

            # if bits_list[i-1] == "1":
            #     qc.x(q0)

            # apply Hadamard on the auxiiliary qubit
            qc.h(q0)
            qc.x(q1)
            ##2 Apply phase correction conditioned on the first classical bit
            for j in range(i):
                if bits_list[j] == "1":
                    qc.p((-2*np.pi)/(2**(i-j+1)), q0)
            ##3 Apply control-U operator as many times as needed to get the next phase bit
            # we want to apply controlled-S 2^k times
            k = steps - i - 1
            # calculate the angle of CPhase corresponding to 2^k applications of controlled-S
            cphase_angle = angle * 2**k
            # apply the controlled phase gate
            qc.cp(cphase_angle, q0, q1)
            ##4 Measure the auxiliary qubit in x-basis into the second classical bit
            # apply Hadamard to change to the X basis
            qc.h(q0)
            # measure the auxiliary qubit into the first classical bit
            qc.measure(q0, list[0])
            sim = AerSimulator()
            job = sim.run(qc, noise_model=noise_model, shots=shots_per_it[i])
            result = job.result()
            counts = result.get_counts()
            max_val = max(counts.values())
            max_keys = []
            for key in counts:
                if counts[key] == max_val:
                    max_keys.append(key)
            chosen_one = max_keys[0]
            bits_list.append(chosen_one)
        return iqpe(angle, steps , bits_list)

#Funktioniert
def convert(bin: str):                  #konvertiert den bitstring in deciaml, e.g. 0110 = 0.375
    k = list(bin)
    a = [int(i) for i in k]
    n = 0
    for i in range(len(a)):
        if a[i] == 1:
            n += 1/2**(i+1)
    return n
#Funktioniert

def closest_bin(n: float, prec: int):           #Gibt einem den nächsten binären Nachbarn zu einem Float an bei gegebener Präzision/Depth
    closest = 10
    steps = 2**(-prec)
    bin_list = [i*steps for i in range(2**prec+1)]
    for i in bin_list:
        if np.abs(n - i) < np.abs(closest-n):
            closest = i
    return closest
#Funktioniert

def plot_closest_bin_per_depth(n: float, maxdepth: int):            #Plottet wie sich die binären Nachbarn bei einem Float ändern für unterschiedliche Präzision/Depth
    x = [i for i in range(maxdepth)]
    y_old = [closest_bin(n,i) for i in range(maxdepth)]
    y = [0]
    for i in range(len(x)-1):
        y.append(y_old[i+1]-y_old[i])
    
    invalid = []
    for i in range(len(x)):
        if y[i] == 0:
            invalid.append(x[i])
    invalid_y = [0 for i in invalid]
    fig, ax = plt.subplots(figsize=(12,6))
    plt.plot(x,y,"x",linestyle="dotted")
    plt.plot(invalid, invalid_y, "x", color = "red", label="No change of binary neighbour")
    plt.xlabel("Depth")
    plt.ylabel("Difference between current and previous binary neighbour")
    plt.title("Änderung der binären Nachbarn für versch. Präzisionen für die Zahl {}".format(n))
    plt.legend()
#Funktioniert

def convert(bin: str):                  #konvertiert den bitstring in deciaml, e.g. 0110 = 0.375
    k = list(bin)
    a = [int(i) for i in k]
    n = 0
    for i in range(len(a)):
        if a[i] == 1:
            n += 1/2**(i+1)
    return n


def gen_data(name, angle: float, shots: int, depth: int, steps: int, shots_per_it = 10):
    theta = 2*np.pi*angle
    soweit = 0.4
    x = np.linspace(0,soweit,steps)
    error = np.linspace(0,soweit,steps)
    y = np.zeros(steps)
    for k in range(steps):
        p = error[k]
        p_error = pauli_error([["X",p/2],["I",1-p],["Z",p/2]])
        p_error_2 = pauli_error([["XX",p/6],["XI",p/6],["IX",p/6],["II",1-p],["ZZ",p/6],["ZI",p/6],["IZ",p/6]])

        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(p_error, ['x', 'h', "p"])  # Apply to single-qubit gates
        noise_model.add_all_qubit_quantum_error(p_error_2, ['cp'])  # Apply to 2-qubit gates

        listt = [shots_per_it for i in range(depth-1)]
        qc = iqpe_improved_noisy(theta, noise_model,listt)
        sim = AerSimulator()
        job = sim.run(qc, noise_model=noise_model, shots=shots)
        result = job.result()
        counts = result.get_counts()
        keys = counts.keys()
        values = counts.values()
        keys = [convert(i) for i in keys]
        values = [i for i in values]
        most = convert(max(counts, key=counts.get))
        prec = np.abs(most-angle)
        #x.append(error_1[i])
        y[k] = prec

    data = np.array((x,y))
    np.savetxt("dat_iQPE+_err_thresh{}.txt".format(name), data, delimiter=",")