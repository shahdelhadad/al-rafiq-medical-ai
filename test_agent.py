from main import agent

print("\n--- Test: Dummy Data Queries ---")

response = agent.run("Find patient named Ahmed Ali")
print("\nPatient Search Response:", response)

response = agent.run("Show me doctor named Dr. Omar Khaled")
print("\nDoctor Search Response:", response)

response = agent.run("What prescription does Ahmed Ali have?")
print("\nPrescription Search Response:", response)

response = agent.run("When is Ahmed Ali's next appointment?")
print("\nAppointment Search Response:", response)

print("\n--- End of Test ---\n")
