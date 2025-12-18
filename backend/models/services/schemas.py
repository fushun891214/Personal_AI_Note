"""
Service 層使用的 Schema 定義
"""

# 定義 Notion Blocks 的 JSON Schema
NOTION_BLOCKS_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "論文標題（精簡版，15字內）"
        },
        "blocks": {
            "type": "array",
            "description": "Notion blocks 陣列，包含論文導讀的所有內容",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["callout", "heading_2", "heading_3", "bulleted_list_item", "code", "quote", "toggle"]
                    },
                    "callout": {
                        "type": "object",
                        "properties": {
                            "icon": {
                                "type": "object",
                                "properties": {
                                    "emoji": {"type": "string"}
                                },
                                "required": ["emoji"]
                            },
                            "rich_text": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["text"]},
                                        "text": {
                                            "type": "object",
                                            "properties": {
                                                "content": {"type": "string"}
                                            },
                                            "required": ["content"]
                                        },
                                        "annotations": {
                                            "type": "object",
                                            "properties": {
                                                "bold": {"type": "boolean"},
                                                "italic": {"type": "boolean"},
                                                "code": {"type": "boolean"}
                                            }
                                        }
                                    },
                                    "required": ["type", "text"]
                                }
                            }
                        },
                        "required": ["icon", "rich_text"]
                    },
                    "heading_2": {
                        "type": "object",
                        "properties": {
                            "rich_text": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["text"]},
                                        "text": {
                                            "type": "object",
                                            "properties": {
                                                "content": {"type": "string"}
                                            },
                                            "required": ["content"]
                                        }
                                    },
                                    "required": ["type", "text"]
                                }
                            }
                        },
                        "required": ["rich_text"]
                    },
                    "heading_3": {
                        "type": "object",
                        "properties": {
                            "rich_text": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["text"]},
                                        "text": {
                                            "type": "object",
                                            "properties": {
                                                "content": {"type": "string"}
                                            },
                                            "required": ["content"]
                                        }
                                    },
                                    "required": ["type", "text"]
                                }
                            }
                        },
                        "required": ["rich_text"]
                    },
                    "bulleted_list_item": {
                        "type": "object",
                        "properties": {
                            "rich_text": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["text"]},
                                        "text": {
                                            "type": "object",
                                            "properties": {
                                                "content": {"type": "string"}
                                            },
                                            "required": ["content"]
                                        },
                                        "annotations": {
                                            "type": "object",
                                            "properties": {
                                                "bold": {"type": "boolean"}
                                            }
                                        }
                                    },
                                    "required": ["type", "text"]
                                }
                            }
                        },
                        "required": ["rich_text"]
                    },
                    "code": {
                        "type": "object",
                        "properties": {
                            "language": {
                                "type": "string",
                                "enum": ["python", "javascript", "typescript", "java", "c", "c++", "c#", "go", "rust", "ruby", "php", "swift", "kotlin", "bash", "shell", "powershell", "sql", "html", "css", "json", "yaml", "xml", "markdown", "plain text", "latex"]
                            },
                            "rich_text": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["text"]},
                                        "text": {
                                            "type": "object",
                                            "properties": {
                                                "content": {"type": "string"}
                                            },
                                            "required": ["content"]
                                        }
                                    },
                                    "required": ["type", "text"]
                                }
                            }
                        },
                        "required": ["language", "rich_text"]
                    },
                    "quote": {
                        "type": "object",
                        "properties": {
                            "rich_text": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["text"]},
                                        "text": {
                                            "type": "object",
                                            "properties": {
                                                "content": {"type": "string"}
                                            },
                                            "required": ["content"]
                                        }
                                    },
                                    "required": ["type", "text"]
                                }
                            }
                        },
                        "required": ["rich_text"]
                    },
                    "toggle": {
                        "type": "object",
                        "properties": {
                            "rich_text": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["text"]},
                                        "text": {
                                            "type": "object",
                                            "properties": {
                                                "content": {"type": "string"}
                                            },
                                            "required": ["content"]
                                        }
                                    },
                                    "required": ["type", "text"]
                                }
                            },
                            "children": {
                                "type": "array",
                                "description": "Toggle 內的子 blocks（通常是 bulleted_list_item）",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["bulleted_list_item"]
                                        },
                                        "bulleted_list_item": {
                                            "type": "object",
                                            "properties": {
                                                "rich_text": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "type": {"type": "string", "enum": ["text"]},
                                                            "text": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "content": {"type": "string"}
                                                                },
                                                                "required": ["content"]
                                                            },
                                                            "annotations": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "bold": {"type": "boolean"}
                                                                }
                                                            }
                                                        },
                                                        "required": ["type", "text"]
                                                    }
                                                }
                                            },
                                            "required": ["rich_text"]
                                        }
                                    },
                                    "required": ["type", "bulleted_list_item"]
                                }
                            }
                        },
                        "required": ["rich_text", "children"]
                    }
                },
                "required": ["type"]
            }
        }
    },
    "required": ["title", "blocks"]
}
