
def theme(request):
    # TODO - check what the system/browser default theme is and use that if it is available.
    #        we might need to use JS to detect that on the client side though.
    if 'is_dark_theme' in request.session:
        is_dark_theme = request.session.get("is_dark_theme")
        return {"is_dark_theme": is_dark_theme}    
    return {"is_dark_theme": False}