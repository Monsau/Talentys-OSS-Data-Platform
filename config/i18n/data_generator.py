#!/usr/bin/env python3
"""
Générateur de données multilingue
Support: EN, FR, ES, PT, AR, CN, JP, RU
"""

from faker import Faker
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List

class MultilingualDataGenerator:
    """Générateur de données avec support multilingue"""
    
    LOCALES = {
        'en': 'en_US',
        'fr': 'fr_FR',
        'es': 'es_ES',
        'pt': 'pt_BR',
        'ar': 'ar_SA',
        'cn': 'zh_CN',
        'jp': 'ja_JP',
        'ru': 'ru_RU'
    }
    
    def __init__(self, language: str = 'en', num_records: int = 100):
        """
        Initialiser le générateur
        
        Args:
            language: Code langue (en, fr, es, pt, ar, cn, jp, ru)
            num_records: Nombre d'enregistrements à générer
        """
        locale = self.LOCALES.get(language, 'en_US')
        self.fake = Faker(locale)
        self.language = language
        self.num_records = num_records
        
    def generate_customers(self) -> pd.DataFrame:
        """Générer données clients"""
        data = []
        for _ in range(self.num_records):
            data.append({
                'id': self.fake.uuid4(),
                'name': self.fake.name(),
                'email': self.fake.email(),
                'phone': self.fake.phone_number(),
                'address': self.fake.address().replace('\n', ', '),
                'city': self.fake.city(),
                'country': self.fake.country(),
                'company': self.fake.company(),
                'job_title': self.fake.job(),
                'created_at': self.fake.date_time_this_year().isoformat(),
                'language': self.language
            })
        return pd.DataFrame(data)
    
    def generate_products(self) -> pd.DataFrame:
        """Générer données produits"""
        data = []
        for _ in range(self.num_records):
            data.append({
                'id': self.fake.uuid4(),
                'name': self.fake.catch_phrase(),
                'description': self.fake.text(max_nb_chars=200),
                'price': round(self.fake.random.uniform(10, 1000), 2),
                'category': self.fake.word(),
                'created_at': self.fake.date_time_this_year().isoformat(),
                'language': self.language
            })
        return pd.DataFrame(data)
    
    def save(self, df: pd.DataFrame, output_dir: Path, filename: str, format: str = 'csv'):
        """Sauvegarder données"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if format == 'csv':
            output_path = output_dir / f"{filename}.csv"
            df.to_csv(output_path, index=False, encoding='utf-8')
        elif format == 'json':
            output_path = output_dir / f"{filename}.json"
            df.to_json(output_path, orient='records', force_ascii=False, indent=2)
        elif format == 'parquet':
            output_path = output_dir / f"{filename}.parquet"
            df.to_parquet(output_path, index=False, compression='snappy')
        
        print(f"✅ Saved: {output_path}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate multilingual test data')
    parser.add_argument('--language', '-l', default='en', 
                       choices=['en', 'fr', 'es', 'pt', 'ar', 'cn', 'jp', 'ru'],
                       help='Language code')
    parser.add_argument('--records', '-n', type=int, default=100,
                       help='Number of records')
    parser.add_argument('--format', '-f', default='csv',
                       choices=['csv', 'json', 'parquet'],
                       help='Output format')
    parser.add_argument('--output', '-o', default='data/generated',
                       help='Output directory')
    
    args = parser.parse_args()
    
    generator = MultilingualDataGenerator(args.language, args.records)
    output_dir = Path(args.output) / args.language
    
    # Generate datasets
    print(f"\n🌍 Generating data in {generator.LOCALES[args.language]}...")
    
    customers = generator.generate_customers()
    generator.save(customers, output_dir, 'customers', args.format)
    
    products = generator.generate_products()
    generator.save(products, output_dir, 'products', args.format)
    
    print(f"\n✅ Generated {args.records} records in {args.language}")
