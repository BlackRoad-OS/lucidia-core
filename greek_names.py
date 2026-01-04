"""Greek name generator for BlackRoad agents and systems.

This module generates random Greek names for agents, repositories, and
components in the BlackRoad ecosystem. Each name is unique and tracked.
"""

import hashlib
import random
import time
from typing import Optional


# Greek deity and hero names
GREEK_NAMES = [
    # Olympian deities
    "Zeus", "Hera", "Poseidon", "Demeter", "Athena", "Apollo",
    "Artemis", "Ares", "Aphrodite", "Hephaestus", "Hermes", "Dionysus",
    # Titans
    "Cronus", "Rhea", "Oceanus", "Tethys", "Hyperion", "Theia",
    "Coeus", "Phoebe", "Mnemosyne", "Themis", "Crius", "Iapetus",
    # Primordial deities
    "Chaos", "Gaia", "Tartarus", "Eros", "Erebus", "Nyx",
    "Aether", "Hemera", "Pontus", "Uranus",
    # Heroes and mortals
    "Heracles", "Perseus", "Theseus", "Achilles", "Odysseus", "Jason",
    "Orpheus", "Cadmus", "Bellerophon", "Meleager",
    # Muses
    "Calliope", "Clio", "Erato", "Euterpe", "Melpomene",
    "Polyhymnia", "Terpsichore", "Thalia", "Urania",
    # Other deities
    "Hades", "Persephone", "Hecate", "Pan", "Helios", "Selene",
    "Eos", "Nike", "Tyche", "Nemesis", "Morpheus", "Hypnos",
    # Nymphs and spirits
    "Daphne", "Echo", "Calypso", "Circe", "Medea", "Ariadne",
    "Psyche", "Aura", "Harmonia", "Iris", "Hebe", "Ganymede",
    # Additional heroes
    "Ajax", "Nestor", "Patroclus", "Diomedes", "Agamemnon",
    "Menelaus", "Hector", "Aeneas", "Priam", "Cassandra",
    # Philosophers and scholars
    "Pythagoras", "Heraclitus", "Parmenides", "Empedocles", "Anaxagoras",
    "Democritus", "Socrates", "Plato", "Aristotle", "Euclid",
    "Archimedes", "Ptolemy", "Hypatia", "Thales", "Epicurus",
]

# Greek suffixes for variation
SUFFIXES = ["os", "is", "as", "eus", "ion", "on", "ides", "ias"]

# Greek prefixes for variation
PREFIXES = ["Neo", "Proto", "Auto", "Hyper", "Meta", "Mega", "Poly", "Chrono"]


class GreekNameGenerator:
    """Generate unique Greek names for BlackRoad agents."""

    def __init__(self, seed: Optional[int] = None):
        """Initialize the name generator.
        
        Args:
            seed: Optional random seed for reproducibility
        """
        self._used_names = set()
        self._seed = seed or int(time.time())
        random.seed(self._seed)

    def generate(self, prefix: Optional[str] = None, 
                 suffix: Optional[str] = None,
                 variant: bool = False) -> str:
        """Generate a unique Greek name.
        
        Args:
            prefix: Optional prefix to add to name
            suffix: Optional suffix to add to name
            variant: If True, create variant names with prefixes/suffixes
            
        Returns:
            A unique Greek name
        """
        max_attempts = 1000
        for _ in range(max_attempts):
            if variant:
                # Create variant with prefix/suffix
                base_name = random.choice(GREEK_NAMES)
                if random.random() > 0.5:
                    name = random.choice(PREFIXES) + base_name
                else:
                    # Remove last few chars and add suffix
                    name = base_name[:-2] + random.choice(SUFFIXES)
            else:
                name = random.choice(GREEK_NAMES)
            
            if prefix:
                name = prefix + name
            if suffix:
                name = name + suffix
                
            if name not in self._used_names:
                self._used_names.add(name)
                return name
        
        # Fallback to hash-based name
        return self._generate_hash_based_name()

    def _generate_hash_based_name(self) -> str:
        """Generate a hash-based unique name as fallback."""
        timestamp = str(time.time())
        hash_val = hashlib.sha256(timestamp.encode()).hexdigest()[:8]
        name = f"Agent{hash_val.upper()}"
        self._used_names.add(name)
        return name

    def generate_agent_name(self, agent_type: str = "Agent") -> str:
        """Generate a name specifically for an agent.
        
        Args:
            agent_type: Type of agent (e.g., "Physicist", "Mathematician")
            
        Returns:
            A unique agent name
        """
        return self.generate(prefix=agent_type, variant=True)

    def generate_repository_name(self) -> str:
        """Generate a name for a repository."""
        return self.generate(suffix="Core", variant=True)

    def generate_module_name(self) -> str:
        """Generate a name for a module."""
        return self.generate(suffix="Module", variant=False)

    def reset(self):
        """Reset the used names set."""
        self._used_names.clear()

    @property
    def used_names(self) -> set:
        """Get all generated names."""
        return self._used_names.copy()


# Global generator instance
_global_generator = GreekNameGenerator()


def generate_name(prefix: Optional[str] = None, 
                  suffix: Optional[str] = None,
                  variant: bool = False) -> str:
    """Generate a unique Greek name using the global generator.
    
    Args:
        prefix: Optional prefix to add to name
        suffix: Optional suffix to add to name
        variant: If True, create variant names with prefixes/suffixes
        
    Returns:
        A unique Greek name
    """
    return _global_generator.generate(prefix, suffix, variant)


def generate_agent_name(agent_type: str = "Agent") -> str:
    """Generate a name specifically for an agent.
    
    Args:
        agent_type: Type of agent
        
    Returns:
        A unique agent name
    """
    return _global_generator.generate_agent_name(agent_type)


if __name__ == "__main__":
    # Demo usage
    gen = GreekNameGenerator()
    
    print("Sample Greek names for agents:")
    for i in range(10):
        print(f"  {i+1}. {gen.generate_agent_name('BlackRoad')}")
    
    print("\nSample repository names:")
    for i in range(5):
        print(f"  {i+1}. {gen.generate_repository_name()}")
    
    print(f"\nTotal names generated: {len(gen.used_names)}")
