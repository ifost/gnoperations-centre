# Why the special module?  Just to make things seem more
# friendly on other platforms.
# Also, I didn't need to full generality of getopt.
import string

def gnpcGetOpt(argument_list,option_dictionary):
    """Takes a list,  and breaks it up into (parsed_options,remainder),
    where parsed_options is a dictionary of the arguments found.
    Acceptable pre-thingies are  -- - /,  and acceptable post-thingies
    are = : <nextarg>"""
    result = {}
    i = 0

    while i < len(argument_list):
        arg = argument_list[i]
        middle = get_prefix(arg)
        if middle is None:
            return (result,argument_list[i:])
        (word,rhs) = get_word(middle)
        if option_dictionary.has_key(word):
            if rhs is None:
                i=i+1
                try:
                    result[option_dictionary[word]] = argument_list[i]
                except IndexError:
                    return (result,argument_list[i-1:])
            else:
                result[option_dictionary[word]] = rhs
        
        i=i+1
    return (result,[])
        
        
pre_thingy = ['--','-','/']
post_thingy = ['=',':']

def get_prefix(x):
    if len(x)>2 and (x[0:2]=='--'): return x[2:]
    if len(x)>1 and (x[0]=='-'): return x[1:]
    if len(x)>1 and (x[0]=='/'): return x[1:]
    return None

def get_word(x):
    equals_sign = string.find(x,'=')
    colon = string.find(x,':')
    if (equals_sign == -1) and (colon == -1):
        return (x,None)
    if (equals_sign == -1) or ((colon != -1) and (colon < equals_sign)):
        return (x[:colon],x[colon+1:])
    if (colon == -1) or (equals_sign < colon):
        return (x[:equals_sign],x[equals_sign+1:])
    raise IndexError,(colon,equals_sign,x)
    
    
    
    
    
