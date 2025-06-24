#!/usr/bin/env python3
import json
import csv
import sys
import os
import argparse
from typing import Dict, List, Any

def load_json_data(json_file_path: str) -> Dict[str, Any]:
    """JSONファイルを読み込む"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: JSONファイル '{json_file_path}' が見つかりません")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error: JSONファイルの読み込みエラー: {e}")
        return {}

def generate_nodes_csv(nodes_data: List[Dict[str, Any]], output_file: str = "nodes_ln.csv"):
    """ノード情報からnodes_ln.csvを生成"""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id'])  # ヘッダー
        
        for node in nodes_data:
            pub_key = node.get('pub_key', '')
            writer.writerow([pub_key])
    
    print(f"Generated {output_file} with {len(nodes_data)} nodes")

def generate_channels_csv(edges_data: List[Dict[str, Any]], output_file: str = "channels_ln.csv"):
    """エッジ情報からchannels_ln.csvを生成"""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'edge1_id', 'edge2_id', 'node1_id', 'node2_id', 'capacity(millisat)'])
        
        for edge in edges_data:
            channel_id = edge.get('channel_id', '')
            node1_pub = edge.get('node1_pub', '')
            node2_pub = edge.get('node2_pub', '')
            capacity = edge.get('capacity', '0')
            
            # エッジIDを生成 (channel_id + 方向を示すサフィックス)
            edge1_id = f"{channel_id}_1"  # node1からnode2への方向
            edge2_id = f"{channel_id}_2"  # node2からnode1への方向
            
            writer.writerow([channel_id, edge1_id, edge2_id, node1_pub, node2_pub, capacity])
    
    print(f"Generated {output_file} with {len(edges_data)} channels")

def generate_edges_csv(edges_data: List[Dict[str, Any]], output_file: str = "edges_ln.csv"):
    """エッジ情報からedges_ln.csvを生成（両方向のポリシーを別々の行として出力）"""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'id', 'channel_id', 'counter_edge_id', 'from_node_id', 'to_node_id', 
            'balance(millisat)', 'fee_base(millisat)', 'fee_proportional', 
            'min_htlc(millisat)', 'timelock'
        ])
        
        for edge in edges_data:
            channel_id = edge.get('channel_id', '')
            node1_pub = edge.get('node1_pub', '')
            node2_pub = edge.get('node2_pub', '')
            
            edge1_id = f"{channel_id}_1"
            edge2_id = f"{channel_id}_2"
            
            # Node1のポリシー (node1 -> node2)
            node1_policy = edge.get('node1_policy', {})
            if node1_policy:
                writer.writerow([
                    edge1_id,
                    channel_id,
                    edge2_id,  # counter edge
                    node1_pub,  # from_node_id
                    node2_pub,  # to_node_id
                    '',  # balance (JSONにはないのでデフォルトで空)
                    node1_policy.get('fee_base_msat', '0'),
                    node1_policy.get('fee_rate_milli_msat', '0'),
                    node1_policy.get('min_htlc', '0'),
                    node1_policy.get('time_lock_delta', '0')
                ])
            
            # Node2のポリシー (node2 -> node1)
            node2_policy = edge.get('node2_policy', {})
            if node2_policy:
                writer.writerow([
                    edge2_id,
                    channel_id,
                    edge1_id,  # counter edge
                    node2_pub,  # from_node_id
                    node1_pub,  # to_node_id
                    '',  # balance (JSONにはないのでデフォルトで空)
                    node2_policy.get('fee_base_msat', '0'),
                    node2_policy.get('fee_rate_milli_msat', '0'),
                    node2_policy.get('min_htlc', '0'),
                    node2_policy.get('time_lock_delta', '0')
                ])
    
    print(f"Generated {output_file} with {len(edges_data) * 2} edge policies")

def main():
    """メイン処理"""
    # コマンドライン引数を解析
    parser = argparse.ArgumentParser(description='JSONファイルからCSVファイルを生成します')
    parser.add_argument('json_file', help='入力JSONファイルのパス')
    parser.add_argument('-o', '--output', help='出力ディレクトリ（デフォルト: カレントディレクトリ）', default='.')
    
    args = parser.parse_args()
    
    # 出力ディレクトリが存在しない場合は作成
    if not os.path.exists(args.output):
        os.makedirs(args.output)
        print(f"出力ディレクトリを作成しました: {args.output}")
    
    # JSONデータを読み込み
    data = load_json_data(args.json_file)
    
    if not data:
        print("Error: JSONデータの読み込みに失敗しました")
        return
    
    # 各セクションのデータを取得
    nodes_data = data.get('nodes', [])
    edges_data = data.get('edges', [])
    
    print(f"読み込み完了: {len(nodes_data)} nodes, {len(edges_data)} edges")
    
    # 出力ファイルのパスを構築
    nodes_output = os.path.join(args.output, "nodes_ln.csv")
    channels_output = os.path.join(args.output, "channels_ln.csv")
    edges_output = os.path.join(args.output, "edges_ln.csv")
    
    # 各CSVファイルを生成
    generate_nodes_csv(nodes_data, nodes_output)
    generate_channels_csv(edges_data, channels_output)
    generate_edges_csv(edges_data, edges_output)
    
    print("All CSV files generated successfully!")

if __name__ == "__main__":
    main()

