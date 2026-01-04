"""BlackRoad hashing system for agents, files, and components.

This module provides SHA-256 based hashing for all BlackRoad components
with tracking and verification capabilities.
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class BlackRoadHash:
    """Represents a BlackRoad hash with metadata."""
    
    hash_value: str
    entity_type: str  # "agent", "file", "commit", "module", etc.
    entity_name: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hash": self.hash_value,
            "type": self.entity_type,
            "name": self.entity_name,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "metadata": self.metadata
        }
    
    def __str__(self) -> str:
        return f"BR-{self.entity_type[:3].upper()}-{self.hash_value[:16]}"


class BlackRoadHasher:
    """Generate and manage BlackRoad hashes."""
    
    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize the hasher.
        
        Args:
            registry_path: Path to store hash registry
        """
        self.registry_path = registry_path or Path(".blackroad_hashes.json")
        self._registry: Dict[str, BlackRoadHash] = {}
        self._load_registry()
    
    def hash_content(self, content: str, entity_type: str, 
                     entity_name: str, **metadata) -> BlackRoadHash:
        """Generate a BlackRoad hash for content.
        
        Args:
            content: Content to hash
            entity_type: Type of entity (agent, file, commit, etc.)
            entity_name: Name of the entity
            **metadata: Additional metadata
            
        Returns:
            BlackRoadHash object
        """
        # Create SHA-256 hash with BlackRoad prefix
        hash_obj = hashlib.sha256()
        hash_obj.update(f"BLACKROAD:{entity_type}:{entity_name}:".encode())
        hash_obj.update(content.encode())
        hash_value = hash_obj.hexdigest()
        
        br_hash = BlackRoadHash(
            hash_value=hash_value,
            entity_type=entity_type,
            entity_name=entity_name,
            metadata=metadata
        )
        
        # Store in registry
        self._registry[entity_name] = br_hash
        self._save_registry()
        
        return br_hash
    
    def hash_file(self, file_path: Path, **metadata) -> BlackRoadHash:
        """Generate a BlackRoad hash for a file.
        
        Args:
            file_path: Path to file
            **metadata: Additional metadata
            
        Returns:
            BlackRoadHash object
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.hash_content(
            content=content,
            entity_type="file",
            entity_name=str(file_path),
            file_size=len(content),
            **metadata
        )
    
    def hash_agent(self, agent_name: str, agent_config: Dict[str, Any]) -> BlackRoadHash:
        """Generate a BlackRoad hash for an agent.
        
        Args:
            agent_name: Name of the agent
            agent_config: Agent configuration
            
        Returns:
            BlackRoadHash object
        """
        content = json.dumps(agent_config, sort_keys=True)
        return self.hash_content(
            content=content,
            entity_type="agent",
            entity_name=agent_name,
            config=agent_config
        )
    
    def hash_commit(self, commit_sha: str, commit_message: str, 
                    author: str, **metadata) -> BlackRoadHash:
        """Generate a BlackRoad hash for a git commit.
        
        Args:
            commit_sha: Git commit SHA
            commit_message: Commit message
            author: Commit author
            **metadata: Additional metadata
            
        Returns:
            BlackRoadHash object
        """
        content = f"{commit_sha}:{author}:{commit_message}"
        return self.hash_content(
            content=content,
            entity_type="commit",
            entity_name=commit_sha,
            message=commit_message,
            author=author,
            **metadata
        )
    
    def verify_hash(self, entity_name: str, current_content: str) -> bool:
        """Verify if a hash matches current content.
        
        Args:
            entity_name: Name of entity to verify
            current_content: Current content to verify against
            
        Returns:
            True if hash matches, False otherwise
        """
        if entity_name not in self._registry:
            return False
        
        stored_hash = self._registry[entity_name]
        hash_obj = hashlib.sha256()
        hash_obj.update(f"BLACKROAD:{stored_hash.entity_type}:{entity_name}:".encode())
        hash_obj.update(current_content.encode())
        current_hash = hash_obj.hexdigest()
        
        return current_hash == stored_hash.hash_value
    
    def get_hash(self, entity_name: str) -> Optional[BlackRoadHash]:
        """Get stored hash for an entity.
        
        Args:
            entity_name: Name of entity
            
        Returns:
            BlackRoadHash if found, None otherwise
        """
        return self._registry.get(entity_name)
    
    def list_hashes(self, entity_type: Optional[str] = None) -> List[BlackRoadHash]:
        """List all stored hashes.
        
        Args:
            entity_type: Optional filter by entity type
            
        Returns:
            List of BlackRoadHash objects
        """
        if entity_type:
            return [h for h in self._registry.values() if h.entity_type == entity_type]
        return list(self._registry.values())
    
    def _load_registry(self):
        """Load hash registry from disk."""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r') as f:
                    data = json.load(f)
                    for name, hash_data in data.items():
                        self._registry[name] = BlackRoadHash(
                            hash_value=hash_data["hash"],
                            entity_type=hash_data["type"],
                            entity_name=hash_data["name"],
                            timestamp=hash_data["timestamp"],
                            metadata=hash_data.get("metadata", {})
                        )
            except Exception as e:
                print(f"Warning: Could not load hash registry: {e}")
    
    def _save_registry(self):
        """Save hash registry to disk."""
        try:
            data = {name: hash_obj.to_dict() 
                   for name, hash_obj in self._registry.items()}
            with open(self.registry_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save hash registry: {e}")
    
    def export_registry(self) -> Dict[str, Any]:
        """Export registry as dictionary."""
        return {name: hash_obj.to_dict() 
               for name, hash_obj in self._registry.items()}


# Global hasher instance
_global_hasher = BlackRoadHasher()


def hash_content(content: str, entity_type: str, entity_name: str, 
                 **metadata) -> BlackRoadHash:
    """Generate a BlackRoad hash using global hasher."""
    return _global_hasher.hash_content(content, entity_type, entity_name, **metadata)


def hash_agent(agent_name: str, agent_config: Dict[str, Any]) -> BlackRoadHash:
    """Generate a BlackRoad hash for an agent."""
    return _global_hasher.hash_agent(agent_name, agent_config)


def get_hash(entity_name: str) -> Optional[BlackRoadHash]:
    """Get stored hash for an entity."""
    return _global_hasher.get_hash(entity_name)


if __name__ == "__main__":
    # Demo usage
    hasher = BlackRoadHasher()
    
    # Hash an agent
    agent_hash = hasher.hash_agent(
        "PhysicistAgent",
        {"type": "physicist", "version": "1.0", "domain": "physics"}
    )
    print(f"Agent hash: {agent_hash}")
    
    # Hash a commit
    commit_hash = hasher.hash_commit(
        "abc123def456",
        "Add new feature",
        "developer@blackroad.io"
    )
    print(f"Commit hash: {commit_hash}")
    
    # List all hashes
    print(f"\nAll hashes: {len(hasher.list_hashes())}")
    for h in hasher.list_hashes():
        print(f"  - {h}")
