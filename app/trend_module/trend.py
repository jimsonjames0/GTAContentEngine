from dataclasses import dataclass

#automatically generating the __int__() method
@dataclass
class Trend:
    title: str
    source: str
    url: str
    description: str
    velocity: int
    relevance: int
    novelty: int
    score: int

    #method bound to class itself
    @classmethod
    #cls is for the class, like self is for an instance
    def create(
        cls, 
        title: str,
        source: str,
        url: str,
        description: str,
        velocity: int,
        relevance: int,
        novelty: int,
    ):
        scores = [velocity, relevance, novelty]

        if not all(1 <= score <= 10 for score in scores):
            raise ValueError("Velocity, Relevance, and Novelty must be between 1 and 10")
            
        score = velocity * relevance * novelty

        return cls(
            title = title, 
            source = source, 
            url = url, 
            description = description, 
            velocity = velocity, 
            relevance = relevance, 
            novelty = novelty,
            score = score
        )