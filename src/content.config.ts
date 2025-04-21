// 导入 glob 加载器（loader）
import { glob } from "astro/loaders";
// 从 `astro:content` 导入工具函数
import { z, defineCollection } from "astro:content";

// 定义基础 schema
const baseSchema = {
    title: z.string(),
    pubDate: z.date(),
    // description: z.string(),
    // author: z.string(),
    // image: z.object({
    //     url: z.string(),
    //     alt: z.string()
    // }),
    // tags: z.array(z.string())
};

// 定义集合配置
const collectionDefinitions = {
    // blog: {
    //     pattern: '[^_]*.{md,mdx}',
    //     extraSchema: {}
    // },
    academic: {
        pattern: 'academic/[^_]*.{md,mdx}',
        extraSchema: {
            // ingredients: z.array(z.string()).optional(),
            // difficulty: z.string().optional(),
            // preparationTime: z.string().optional()
        }
    },
    alcohol: {
        pattern: 'alcohol/[^_]*.{md,mdx}',
        extraSchema: {
            // complexity: z.string().optional(),
            // technologies: z.array(z.string()).optional()
        }
    },
    daily: {
        pattern: 'daily/[^_]*.{md,mdx}',
        extraSchema: {
            // complexity: z.string().optional(),
            // technologies: z.array(z.string()).optional()
        }
    }
};

// 创建集合对象
const collections = {};

// 为每个集合定义创建集合
Object.entries(collectionDefinitions).forEach(([name, config]) => {
    collections[name] = defineCollection({
        loader: glob({ pattern: config.pattern, base: "./src/blog" }),
        schema: z.object({
        ...baseSchema,
        ...config.extraSchema
        })
    });
});

// 导出集合
export { collections };