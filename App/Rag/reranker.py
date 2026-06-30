from sentence_transformers import (                #It is a library that provide pre-trained model to generate the relevance score
    CrossEncoder                                   #Query+Document chunks
)

model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"                
)


def rerank(query,results):

    pairs = [ (query, item["text"])               #It is helps to create the pair of query and document chunks for the relevance score
        for item in results
    ]

    scores = model.predict(pairs)                  #It is helps to generate the relevance score for each pair of query and document chunks
    for item, score in zip(                        #It is helps to combine the results and scores together
        results,
        scores
    ):
        item["rerank_score"] = (                    #It is helps to add the relevance score to the results dictionary for each document chunk
            float(score)
        )

    return sorted(                                  #return retrived chunks
        results,                                    #Input list
        key=lambda x:x["rerank_score"],             #Use the rerank score for the sorting           
        reverse=True                                #Sort in descending order
    )[:5]                                           #Return the top 5 