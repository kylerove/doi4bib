from . import import_dois

__all__ = ['add_dois_to_bib']


def add_dois_to_bib(bib_db, logger=None):
    """Enriches a bib database with DOI references.

    DOI references are obtained by contacting the crossref API.

    Args:
        bib_db: a bib databse in the format specified by biblib.
        logger: logger instance
    """

    if len(bib_db.keys()) <= 0:
        return bib_db

    for key, entry in bib_db.items():

        if 'title' in entry.keys():
            title = entry['title']
        else:
            print('There is not a title set for citation-number: ' + entry['citation-number'])
            exit()
        
        if 'journal' in entry.keys():
            journal = entry['journal']
        else:
            journal = None

        if 'date' in entry.keys():
            date = entry['date']
        else:
            date = None
            
        if logger is not None:
            logger.debug(key + ' ' + title)

        if 'pmid' in entry.keys():
            if logger is not None:
                logger.debug(
                        key + ' skipped because pmid entry already present.')
        else:
            ret = import_dois.pubmed_query_title(title,journal,date)
            retries = 0
            #while not ret['success'] and \
            #		retries < import_dois.PUBMED_MAX_RETRIES_ON_ERROR:
            #	retries += 1
            #	ret = import_dois.pubmed_query_title(title,journal,date)
            #	if logger is not None:
            #		logger.debug(key + ' pubmed retry: ' + str(retries))
                    
            if retries < import_dois.PUBMED_MAX_RETRIES_ON_ERROR:
                result = ret["result"]

                if ret['success'] is True:
                    entry.update(pmid=result['pubmed'])
                    
                    if logger is not None:
                        logger.debug(
                                key + ' matched first value')

                else:
                    if logger is not None:
                        logger.debug(
                                key + ' failed match with ' + title)
            else:
                if logger is not None:
                    logger.info(
                            key + ' reached maximum number\
                            of retries contacting PubMed API.')

        if 'doi' in entry.keys():
            if logger is not None:
                logger.debug(
                        key + ' skipped because doi entry already present.')
        else:
            ret = import_dois.crossref_query_title(title)
            retries = 0
            #while not ret['success'] and \
            #		retries < import_dois.MAX_RETRIES_ON_ERROR:
            #	retries += 1
            #	ret = import_dois.crossref_query_title(title)
            #	if logger is not None:
            #		logger.debug(key + ' retry: ' + str(retries))

            if retries < import_dois.MAX_RETRIES_ON_ERROR:
                result = ret["result"]

                if result["similarity"] >= 0.8:
                    entry.update(doi=result['doi'])

                    if logger is not None:
                        logger.debug(
                                key + ' matched with similarity: ' +
                                str(result["similarity"]))
                else:
                    if logger is not None:
                        logger.debug(
                                key + ' failed match with ' +
                                result['crossref_title'] + ' similarity: ' +
                                str(result["similarity"]))
            else:
                if logger is not None:
                    logger.info(
                            key + ' reached maximum number\
                            of retries contacting CrossRef API.')

    return bib_db
