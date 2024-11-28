"""
decryption.py

Provides the class to decrypt database files with wadecrypt.
"""

from pathlib import Path
import subprocess
import os

class Decryptor:
    '''
    Class to decrypt database files.
    '''
    def __init__(self):
        pass

    def _decrypt_file(self, key:str, file_path:Path, output_path:Path):
        '''Helper function to decrypt a single file.'''
        output_file_name = 'decrypted_' + '.'.join(file_path.name.split('.')[:-1]) # removes ".crypt15" from the file name
        subprocess.run(['wadecrypt', key, str(file_path), str(output_path)+r'\\'+output_file_name])


    def decrypt(self, key:str, input_path, output_path=None):
        '''
        Decrypt a single file or all files in a folder.

        Args:
            key (str): Decryption key.
            input_path (str or Path): Path to the file or folder to decrypt.
            output_path (str or Path, optional): Path to save decrypted files. Defaults to a 'decrypted_db' folder.
        '''

        input_path = Path(input_path)
        project_root = Path(__file__).parent.parent
        output_path = project_root / 'decrypted_db' if not output_path else output_path

        if input_path.is_file():
            self._decrypt_file(key, input_path, output_path)
        elif input_path.is_dir(): 
            for file_path in input_path.iterdir(): # contains all child paths
                self._decrypt_file(key, file_path, output_path)
        else : 
            raise ValueError(f"Invalid input path: {input_path}. It must be a file or a folder.")
        
        print(f"Decryption completed. {len(os.listdir(output_path))} files saved to: {output_path}")