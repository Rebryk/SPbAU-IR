import pandas as pd
import math


class Evaluator:
    def __init__(self):
        pass

    def evaluate_to_latex(self,
                          queries_to_evaluate: [str],
                          query_file_path: str,
                          like_file_path: str,
                          relevance_cutoff: int):
        queries_to_evaluate = list(map(str.lower, queries_to_evaluate))
        query_df = pd.DataFrame.from_csv(query_file_path)
        like_df = pd.DataFrame.from_csv(like_file_path)

        # remove redundant queries
        query_df["query"] = query_df["query"].str.lower()
        query_df = query_df[query_df["query"].isin(queries_to_evaluate)]
        like_df = like_df[like_df["query_id"].isin(query_df.index.values)]

        # remove queries with no relevance values
        query_df = query_df[query_df.index.isin(like_df["query_id"])]

        # if for a given query and position there are several relevance values then we choose the latest one
        like_df = like_df.groupby(["query_id", "rank"]).last().reset_index()
        query_ids = {query: query_df[query_df["query"] == query].index.values for query in queries_to_evaluate}

        dcg = {}
        mAP = {}
        reciprocalRank = {}
        result = ["\\begin{tabular}{| l | l | l | l |}", "Query & DCG & MAP & RR \\\\"]
        for query in query_ids:
            dcg[query] = 0
            mAP[query] = 0
            reciprocalRank[query] = 0

            relevant_num = 0
            for rank in range(0, 5):
                select = (like_df["query_id"].isin(query_ids[query])) & (like_df["rank"] == rank)

                mean_relevance = like_df[select]["relevance"].mean()
                print(len(like_df[select]["relevance"]))
                dcg[query] += (2 ** mean_relevance - 1) / math.log(rank + 2)
                if mean_relevance >= relevance_cutoff:
                    relevant_num += 1
                    mAP[query] += relevant_num / (rank + 1)
                    reciprocalRank[query] = max(reciprocalRank[query], 1 / (rank + 1))

            mAP[query] /= relevant_num
            result.append("{} & {:.3f} & {:.3f} & {:.3f} \\\\".format(query, dcg[query], mAP[query], reciprocalRank[query]))
        result.append("\\end{tabular}")
        return "\n".join(result)