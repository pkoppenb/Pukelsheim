import numpy as np

def double_pukelsheim(votes, seats):
    """
    Allocate seats using the Double Pukelsheim algorithm.

    Args:
    - votes (list of floats): List of votes for each party or candidate.
    - seats (int): Total number of seats to allocate.

    Returns:
    - List of integers representing the number of seats allocated to each party or candidate.
    """

    num_parties = len(votes)
    allocated_seats = [0] * num_parties

    while seats > 0:
        quotients = [v / (2 * a + 1) for v, a in zip(votes, allocated_seats)]
        max_quotient_idx = np.argmax(quotients)
        allocated_seats[max_quotient_idx] += 1
        seats -= 1

    return allocated_seats

# Example usage:
votes = [10000, 8000, 6000]  # Example vote counts for 3 parties
total_seats = 10

allocated_seats = double_pukelsheim(votes, total_seats)
print("Allocated Seats:", allocated_seats)
