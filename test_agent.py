from main import agent

print("\n--- Test: Dummy Data Queries ---")

# 1. Test patient search
response = agent.run("Find patient named Ahmed Ali")
print("\nPatient Search Response:", response)

# 2. Test doctor search
response = agent.run("Show me doctor named Dr. Omar Khaled")
print("\nDoctor Search Response:", response)

# 3. Test prescription search
response = agent.run("What prescription does Ahmed Ali have?")
print("\nPrescription Search Response:", response)

# 4. Test appointment search
response = agent.run("When is Ahmed Ali's next appointment?")
print("\nAppointment Search Response:", response)

print("\n--- End of Test ---\n")
