#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业关系图谱可视化
展示专业大类与具体专业之间的语义关系
"""
import json
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Set, Tuple
import math


@dataclass
class MajorNode:
    """专业节点"""
    id: str
    name: str
    type: str  # 'category' | 'major'
    category: str = ""  # 所属大类
    code: str = ""  # 专业代码
    related: List[str] = None  # 关联专业

    def __post_init__(self):
        if self.related is None:
            self.related = []


class MajorRelationGraph:
    """
    专业关系图谱

    构建专业之间的语义关系网络：
    - 大类节点（经济学类）
    - 具体专业节点（经济学、金融学等）
    - 关联关系（同大类、相近专业）
    """

    def __init__(self):
        self.nodes: Dict[str, MajorNode] = {}
        self.edges: List[Tuple[str, str, str]] = []  # (from, to, relation_type)
        self._build_graph()

    def _build_graph(self):
        """构建专业关系图谱"""

        # 定义专业数据结构
        major_data = {
            "经济学类": {
                "code": "0201",
                "majors": [
                    {"name": "经济学", "code": "020101", "related": ["金融学", "财政学"]},
                    {"name": "经济统计学", "code": "020102", "related": ["统计学", "经济学"]},
                    {"name": "国民经济管理", "code": "020103", "related": ["经济学", "管理学"]},
                    {"name": "资源与环境经济学", "code": "020104", "related": ["经济学", "环境科学"]},
                    {"name": "商务经济学", "code": "020105", "related": ["经济学", "国际贸易"]},
                    {"name": "能源经济", "code": "020106", "related": ["经济学", "能源工程"]},
                    {"name": "劳动经济学", "code": "020107", "related": ["经济学", "人力资源管理"]},
                    {"name": "经济工程", "code": "020108", "related": ["经济学", "工程管理"]},
                    {"name": "数字经济", "code": "020109", "related": ["经济学", "数据科学", "计算机"]},
                ]
            },
            "财政学类": {
                "code": "0202",
                "majors": [
                    {"name": "财政学", "code": "020201", "related": ["税收学", "经济学", "金融学"]},
                    {"name": "税收学", "code": "020202", "related": ["财政学", "会计学", "经济学"]},
                    {"name": "国际税收", "code": "020203", "related": ["税收学", "国际经济与贸易"]},
                ]
            },
            "金融学类": {
                "code": "0203",
                "majors": [
                    {"name": "金融学", "code": "020301", "related": ["经济学", "投资学", "保险学"]},
                    {"name": "金融工程", "code": "020302", "related": ["金融学", "数学", "计算机"]},
                    {"name": "保险学", "code": "020303", "related": ["金融学", "精算学"]},
                    {"name": "投资学", "code": "020304", "related": ["金融学", "经济学"]},
                    {"name": "金融数学", "code": "020305", "related": ["金融学", "数学"]},
                    {"name": "信用管理", "code": "020306", "related": ["金融学", "经济学"]},
                    {"name": "经济与金融", "code": "020307", "related": ["经济学", "金融学"]},
                    {"name": "精算学", "code": "020308", "related": ["金融学", "数学", "统计学"]},
                    {"name": "互联网金融", "code": "020309", "related": ["金融学", "计算机"]},
                    {"name": "金融科技", "code": "020310", "related": ["金融学", "计算机", "数据科学"]},
                ]
            },
            "经济与贸易类": {
                "code": "0204",
                "majors": [
                    {"name": "国际经济与贸易", "code": "020401", "related": ["经济学", "商务英语"]},
                    {"name": "贸易经济", "code": "020402", "related": ["经济学", "国际贸易"]},
                ]
            },
            "统计学类": {
                "code": "0712",
                "majors": [
                    {"name": "统计学", "code": "071201", "related": ["数学", "经济学", "数据科学"]},
                    {"name": "应用统计学", "code": "071202", "related": ["统计学", "计算机", "经济学"]},
                    {"name": "数据科学", "code": "071203", "related": ["统计学", "计算机", "数学"]},
                    {"name": "生物统计学", "code": "071204", "related": ["统计学", "生物学", "医学"]},
                ]
            },
            "计算机类": {
                "code": "0809",
                "majors": [
                    {"name": "计算机科学与技术", "code": "080901", "related": ["软件工程", "网络工程"]},
                    {"name": "软件工程", "code": "080902", "related": ["计算机", "网络工程"]},
                    {"name": "网络工程", "code": "080903", "related": ["计算机", "信息安全"]},
                    {"name": "信息安全", "code": "080904", "related": ["计算机", "网络工程"]},
                    {"name": "物联网工程", "code": "080905", "related": ["计算机", "电子"]},
                    {"name": "数字媒体技术", "code": "080906", "related": ["计算机", "设计"]},
                    {"name": "智能科学与技术", "code": "080907", "related": ["计算机", "人工智能"]},
                    {"name": "空间信息与数字技术", "code": "080908", "related": ["计算机", "地理"]},
                    {"name": "电子与计算机工程", "code": "080909", "related": ["计算机", "电子"]},
                    {"name": "数据科学与大数据技术", "code": "080910", "related": ["计算机", "统计学", "数学"]},
                    {"name": "网络空间安全", "code": "080911", "related": ["计算机", "信息安全"]},
                    {"name": "新媒体技术", "code": "080912", "related": ["计算机", "传媒"]},
                    {"name": "电影制作", "code": "080913", "related": ["计算机", "影视"]},
                    {"name": "保密技术", "code": "080914", "related": ["计算机", "信息安全"]},
                    {"name": "服务科学与工程", "code": "080915", "related": ["计算机", "管理"]},
                    {"name": "虚拟现实技术", "code": "080916", "related": ["计算机", "设计"]},
                    {"name": "区块链工程", "code": "080917", "related": ["计算机", "金融"]},
                    {"name": "密码科学与技术", "code": "080918", "related": ["计算机", "数学"]},
                ]
            },
        }

        # 创建节点
        for category, data in major_data.items():
            # 创建大类节点
            cat_id = f"CAT_{data['code']}"
            self.nodes[cat_id] = MajorNode(
                id=cat_id,
                name=category,
                type="category",
                code=data['code']
            )

            # 创建具体专业节点
            for major in data['majors']:
                major_id = f"MAJ_{major['code']}"
                self.nodes[major_id] = MajorNode(
                    id=major_id,
                    name=major['name'],
                    type="major",
                    category=category,
                    code=major['code'],
                    related=major.get('related', [])
                )

                # 添加边：专业 -> 大类
                self.edges.append((major_id, cat_id, "belongs_to"))

                # 添加边：专业之间的关联
                for related_name in major.get('related', []):
                    # 查找相关专业的ID
                    for node_id, node in self.nodes.items():
                        if node.name == related_name and node.type == "major":
                            self.edges.append((major_id, node_id, "related"))
                            break

    def find_path(self, from_major: str, to_major: str) -> List[str]:
        """
        查找两个专业之间的关联路径
        """
        # 找到对应的节点
        from_node = None
        to_node = None

        for node in self.nodes.values():
            if node.name == from_major:
                from_node = node
            if node.name == to_major:
                to_node = node

        if not from_node or not to_node:
            return []

        # 如果同一大类
        if from_node.category == to_node.category and from_node.category:
            return [from_major, f"同属{from_node.category}", to_major]

        # 如果有直接关系
        if to_node.name in from_node.related:
            return [from_major, "相关专业", to_major]

        # 通过大类关联
        if from_node.category and to_node.category:
            return [from_major, from_node.category, "相关大类", to_node.category, to_major]

        return []

    def get_related_majors(self, major_name: str, depth: int = 1) -> Set[str]:
        """
        获取关联专业
        depth: 关联深度
        """
        related = set()

        # 找到起始节点
        start_node = None
        for node in self.nodes.values():
            if node.name == major_name:
                start_node = node
                break

        if not start_node:
            return related

        # 直接关联
        related.add(start_node.name)

        # 同大类专业
        if start_node.category:
            for node in self.nodes.values():
                if node.category == start_node.category and node.type == "major":
                    related.add(node.name)

        # 深度关联
        if depth > 1:
            for rel_name in start_node.related:
                related.add(rel_name)

        return related

    def to_json(self) -> str:
        """导出为JSON格式（用于D3.js可视化）"""
        # 转换节点
        nodes_json = []
        for node in self.nodes.values():
            nodes_json.append({
                "id": node.id,
                "name": node.name,
                "type": node.type,
                "category": node.category,
                "code": node.code,
                "group": self._get_category_code(node.category) if node.category else 0
            })

        # 转换边
        links_json = []
        for edge in self.edges:
            links_json.append({
                "source": edge[0],
                "target": edge[1],
                "type": edge[2]
            })

        return json.dumps({"nodes": nodes_json, "links": links_json}, ensure_ascii=False, indent=2)

    def _get_category_code(self, category: str) -> int:
        """获取大类编号（用于分组颜色）"""
        codes = {
            "经济学类": 1,
            "财政学类": 2,
            "金融学类": 3,
            "经济与贸易类": 4,
            "统计学类": 5,
            "计算机类": 6,
        }
        return codes.get(category, 0)

    def generate_html_visualization(self, output_path: str = "major_graph.html"):
        """
        生成HTML可视化文件
        使用D3.js创建交互式关系图谱
        """
        graph_data = self.to_json()

        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>专业关系图谱 - 智能选岗系统</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            color: white;
            padding: 30px 20px;
        }}
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; font-size: 16px; }}
        .main {{
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 20px;
        }}
        @media (max-width: 900px) {{
            .main {{ grid-template-columns: 1fr; }}
        }}
        .panel {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .panel h3 {{
            margin-bottom: 15px;
            color: #333;
            font-size: 18px;
        }}
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 13px;
        }}
        .legend-color {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        #graph {{
            width: 100%;
            height: 700px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .controls {{
            margin-bottom: 15px;
        }}
        .controls input {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }}
        .info-box {{
            background: #f0f7ff;
            border-left: 4px solid #409eff;
            padding: 15px;
            border-radius: 6px;
            margin-top: 15px;
        }}
        .info-box h4 {{ margin-bottom: 10px; color: #409eff; }}
        .info-box p {{ font-size: 13px; color: #666; line-height: 1.6; }}
        .node-label {{
            font-size: 11px;
            fill: #333;
            pointer-events: none;
        }}
        .link {{
            stroke: #999;
            stroke-opacity: 0.6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 专业关系图谱</h1>
            <p>可视化展示专业大类与具体专业之间的语义关联</p>
        </div>

        <div class="main">
            <div class="panel">
                <h3>📊 图例说明</h3>
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: #ff6b6b;"></div>
                        <span>经济学类</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #4ecdc4;"></div>
                        <span>财政学类</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #45b7d1;"></div>
                        <span>金融学类</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #96ceb4;"></div>
                        <span>经济与贸易类</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #feca57;"></div>
                        <span>统计学类</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #ff9ff3;"></div>
                        <span>计算机类</span>
                    </div>
                </div>

                <h3>🔍 搜索专业</h3>
                <div class="controls">
                    <input type="text" id="searchInput" placeholder="输入专业名称，如：经济学">
                </div>

                <div class="info-box">
                    <h4>💡 使用说明</h4>
                    <p>
                        • 大圆点 = 专业大类（如：经济学类）<br>
                        • 小圆点 = 具体专业（如：经济学）<br>
                        • 连线表示所属关系或专业关联<br>
                        • 拖拽节点可调整布局<br>
                        • 鼠标悬停查看详细信息
                    </p>
                </div>

                <div class="info-box" id="selectedInfo" style="display: none;">
                    <h4>📌 选中专业</h4>
                    <p id="selectedText"></p>
                </div>
            </div>

            <div class="panel">
                <div id="graph"></div>
            </div>
        </div>
    </div>

    <script>
        const graphData = {graph_data};

        const width = document.getElementById('graph').clientWidth;
        const height = 700;

        // 颜色映射
        const colorMap = {{
            0: '#95a5a6',
            1: '#ff6b6b',  // 经济学类
            2: '#4ecdc4',  // 财政学类
            3: '#45b7d1',  // 金融学类
            4: '#96ceb4',  // 经济与贸易类
            5: '#feca57',  // 统计学类
            6: '#ff9ff3',  // 计算机类
        }};

        const svg = d3.select('#graph')
            .append('svg')
            .attr('width', width)
            .attr('height', height);

        // 添加缩放
        const g = svg.append('g');
        svg.call(d3.zoom()
            .extent([[0, 0], [width, height]])
            .scaleExtent([0.5, 4])
            .on('zoom', (event) => g.attr('transform', event.transform)));

        // 创建力导向模拟
        const simulation = d3.forceSimulation(graphData.nodes)
            .force('link', d3.forceLink(graphData.links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(d => d.type === 'category' ? 40 : 25));

        // 绘制连线
        const link = g.append('g')
            .selectAll('line')
            .data(graphData.links)
            .enter().append('line')
            .attr('class', 'link')
            .attr('stroke-width', d => d.type === 'belongs_to' ? 2 : 1)
            .attr('stroke-dasharray', d => d.type === 'related' ? '5,5' : null);

        // 绘制节点
        const node = g.append('g')
            .selectAll('g')
            .data(graphData.nodes)
            .enter().append('g')
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));

        // 节点圆圈
        node.append('circle')
            .attr('r', d => d.type === 'category' ? 30 : 18)
            .attr('fill', d => colorMap[d.group] || '#95a5a6')
            .attr('stroke', '#fff')
            .attr('stroke-width', 2)
            .style('cursor', 'pointer');

        // 节点文字
        node.append('text')
            .attr('class', 'node-label')
            .attr('dy', d => d.type === 'category' ? 45 : 28)
            .attr('text-anchor', 'middle')
            .text(d => d.name.length > 6 ? d.name.substring(0, 5) + '...' : d.name);

        // 鼠标交互
        node.on('mouseover', function(event, d) {{
            d3.select(this).select('circle').attr('stroke', '#333').attr('stroke-width', 3);

            // 高亮相关节点
            const connected = new Set();
            graphData.links.forEach(l => {{
                if (l.source.id === d.id) connected.add(l.target.id);
                if (l.target.id === d.id) connected.add(l.source.id);
            }});

            node.style('opacity', n => n.id === d.id || connected.has(n.id) ? 1 : 0.2);
            link.style('opacity', l => l.source.id === d.id || l.target.id === d.id ? 1 : 0.1);
        }})
        .on('mouseout', function() {{
            d3.select(this).select('circle').attr('stroke', '#fff').attr('stroke-width', 2);
            node.style('opacity', 1);
            link.style('opacity', 1);
        }})
        .on('click', function(event, d) {{
            const info = document.getElementById('selectedInfo');
            const text = document.getElementById('selectedText');
            info.style.display = 'block';

            let html = `<strong>名称：</strong>${{d.name}}<br>`;
            html += `<strong>类型：</strong>${{d.type === 'category' ? '专业大类' : '具体专业'}}<br>`;
            if (d.code) html += `<strong>代码：</strong>${{d.code}}<br>`;
            if (d.category) html += `<strong>所属大类：</strong>${{d.category}}<br>`;

            // 查找关联专业
            const related = graphData.links
                .filter(l => l.source.id === d.id || l.target.id === d.id)
                .map(l => l.source.id === d.id ? l.target.name : l.source.name);

            if (related.length > 0) {{
                html += `<strong>关联专业：</strong>${{related.slice(0, 5).join('、')}}`;
            }}

            text.innerHTML = html;
        }});

        // 搜索功能
        document.getElementById('searchInput').addEventListener('input', function(e) {{
            const keyword = e.target.value.trim();
            if (!keyword) {{
                node.style('opacity', 1);
                link.style('opacity', 1);
                return;
            }}

            node.style('opacity', d => d.name.includes(keyword) ? 1 : 0.1);
            link.style('opacity', 0.1);
        }});

        // 更新位置
        simulation.on('tick', () => {{
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node.attr('transform', d => `translate(${{d.x}},${{d.y}})`);
        }});

        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}

        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}

        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
    </script>
</body>
</html>'''

        # 替换数据
        html_content = html_content.replace('{graph_data}', graph_data)

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path


def main():
    """主函数"""
    print("=" * 80)
    print("专业关系图谱生成器")
    print("=" * 80)

    # 创建图谱
    graph = MajorRelationGraph()

    print(f"\n图谱统计:")
    print(f"  节点数: {len(graph.nodes)}")
    print(f"  关系数: {len(graph.edges)}")

    # 测试路径查找
    print("\n路径查找测试:")
    test_paths = [
        ("经济学", "金融学"),
        ("统计学", "经济学"),
        ("财政学", "金融学"),
    ]

    for from_maj, to_maj in test_paths:
        path = graph.find_path(from_maj, to_maj)
        print(f"  {from_maj} → {to_maj}: {' → '.join(path) if path else '无直接路径'}")

    # 生成可视化
    output_file = "major_graph.html"
    graph.generate_html_visualization(output_file)

    print(f"\n可视化文件已生成: {output_file}")
    print(f"  文件大小: {os.path.getsize(output_file) / 1024:.1f} KB")
    print(f"\n用浏览器打开查看交互式图谱")

    return graph


if __name__ == "__main__":
    graph = main()
