from core.logger import Logger
from core.fetcher import Fetcher
from core.urlmanager import URLManager
from core.storage import *
from core.parser import Parser

import pandas as pd
from datetime import datetime


MAX_DEPTH = 1

if __name__ == "__main__":
    logger = Logger()
    fetcher = Fetcher(logger=logger)
    manager = URLManager()

    #Import dataset of urls and keep only standalone rows (remove na)
    path = "data/domains_annotated.csv"
    df = (pd.read_csv(path)
          .loc[lambda df: df["category"] == "standalone_domain"]
          .dropna(subset=["About Page", "Product Listing Page"])
          .head(5)
          )

    records = []
    #Loop through the dataset and add About and Product Urls and types
    for _, row in df.iterrows():
        about_url = row.get("About Page")
        product_url = row.get("Product Listing Page")
        
        record = {
            "about_url": None,
            "about_path": None,
            "product_url": None,
            "product_path": None,
            "products": []
        }

        manager.add(about_url, "about", depth = 0)
        record["about_url"] = about_url
        record["about_path"] = make_filename(about_url)

        manager.add(product_url, "product", depth = 0)
        record["product_url"] = product_url
        record["product_path"] = make_filename(product_url)
        
        records.append(record)

    while True:
        pending = manager.get_pending()
        if not pending:
            break

        for record in pending:
            url = record["url"]
            page_type = record["url_type"]
            depth_level = record["depth"]

            logger.info(f"[PROCESSING] {page_type} | {url}")

            html = fetcher.fetch(url)

            filepath = None

            if html:
                #Save html
                folder_html = make_filename(url)
                
                #If product url then 
                if page_type == "product":
                    parser = Parser(html)

                    root_folder = f"html/products/{folder_html}"
                    os.makedirs(f"data/{root_folder}", exist_ok=True)
                    
                    filepath = save(html, "main.html", subfolder=root_folder)

                    links = parser.parse_product_links()

                    if depth_level < MAX_DEPTH:
                        for i, link in enumerate(links):
                            depth_folder = make_filename(link)
                            
                            sub_folder = f"{root_folder}/{depth_folder}"
                            os.makedirs(f"data/{sub_folder}", exist_ok=True)

                            product_entry = {
                                "product_url": link,
                                "product_path": f"data/{sub_folder}/main.html",
                                "parent_url": url
                            }

                            sub_html = fetcher.fetch(link)
                            if sub_html:
                                save(sub_html, "main.html", subfolder=sub_folder)
                                logger.info(f"[SAVED] depth=1 | {link}")
                                append_jsonl({
                                    "url": link,
                                    "page_type": "product",
                                    "depth": 1,
                                    "parent_url": url,
                                    "status": "success",
                                    "file": f"data/{sub_folder}/main.html",
                                    "timestamp": datetime.utcnow().isoformat()
                                })
                            else:
                                logger.warning(f"[FAILED] depth=1 | {link}")
                                append_jsonl({
                                    "url": link,
                                    "page_type": "product",
                                    "depth": 1,
                                    "parent_url": url,
                                    "status": "failed",
                                    "timestamp": datetime.utcnow().isoformat()
                                })
                            for r in records:
                                if r["product_url"] == url:
                                    r["products"].append(product_entry)
                

                #If url is about page save in using this path
                elif page_type == "about":
                    filepath = save(html, folder_html+".html", subfolder="html/about/")


            
            
                manager.mark_success(url, filepath)
                append_jsonl({
                    "url": url,
                    "page_type": page_type,
                    "status": "success",
                    "file": filepath,
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                manager.mark_failed(url, "fetch failed")

                append_jsonl({
                    "url": url,
                    "page_type": page_type,
                    "status": "failed",
                    "timestamp": datetime.utcnow().isoformat()
                })

    manager.save("data/url_state.json")
    logger.info("Finished scraping batch.")
    
    mapping_df = pd.DataFrame(records)
    mapping_df.to_csv("data/url_to_filepath.csv", mode="a", header=False, index=False)
