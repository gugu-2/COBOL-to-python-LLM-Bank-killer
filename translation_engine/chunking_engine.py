import re
import logging

class ChunkingEngine:
    """
    Simulates AST parsing by using regex structural heuristics to split massive
    COBOL files into logical chunks (e.g. divisions, sections, paragraphs)
    to prevent LLM context window overflows.
    """
    @staticmethod
    def chunk_cobol_file(cobol_code: str, max_chunk_lines: int = 1000) -> list[str]:
        lines = cobol_code.splitlines()
        
        # If the file is small enough, no chunking needed
        if len(lines) <= max_chunk_lines:
            logging.info("File is small enough. Bypassing chunker.")
            return [cobol_code]
            
        logging.info(f"File exceeds {max_chunk_lines} lines. Applying structural chunking...")
        
        chunks = []
        current_chunk = []
        
        # Heuristic: We want to break at major boundaries if possible.
        # Major boundaries: DIVISIONS, SECTIONS, PARAGRAPHS (lines starting without spaces)
        division_pattern = re.compile(r'^[ \t]*[A-Z0-9\-]+ DIVISION\.')
        
        for line in lines:
            if len(current_chunk) >= max_chunk_lines and division_pattern.match(line):
                # We hit a major boundary and our chunk is full enough, save it
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                
            current_chunk.append(line)
            
        if current_chunk:
            chunks.append("\n".join(current_chunk))
            
        logging.info(f"Chunking Engine split file into {len(chunks)} chunks.")
        return chunks
