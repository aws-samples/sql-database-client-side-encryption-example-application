import logging

from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import CustomerProfileForm
from .models import CustomerProfile

import aws_encryption_sdk

import json

from codecompose import master_key_encryption_provider, master_key_decryption_provider

# Create your views here.
def index(request):
    context={}
    return render(request,'create',context)

def create(request):
    if request.method =='GET':
        form=CustomerProfileForm()
        context={'form': form}
        return render(request, 'create.html', context)

    if request.method=='POST':
        form = CustomerProfileForm(request.POST)
        if not form.is_valid():
            #form error
            context={'form': form}
            return render(request, 'create.html', context)
        elif CustomerProfile.objects.filter(account_number=form.cleaned_data['account_number']).first():
            #account number exists
            form.add_error('account_number',"Account Number already exists")
            context={'form': form}
            return render(request, 'create.html', context)
        else:
            acct=CustomerProfile(account_number=form.cleaned_data['account_number'],userid=form.cleaned_data['userid'])
            encryption_context={'account_number':acct.account_number}
            ciphertext, encryptor_header = aws_encryption_sdk.encrypt(
                source=acct.userid,
                key_provider=master_key_encryption_provider,
                encryption_context=encryption_context
            )
            acct.account_encrypted=ciphertext
            acct.userid="" #clear out, production app wouldn't have this field in the database schema
            logging.info(json.dumps(encryptor_header.encryption_context))
            acct.save()
            return HttpResponseRedirect( 'authenticate' )

def authenticate(request):
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST)
        if not form.is_valid():
            context={'form':form}
            return render(request,"authenticate.html",context)
        else:
            acct=CustomerProfile(account_number=form.cleaned_data['account_number'],userid=form.cleaned_data['userid'])
            try:
                account_in_db=CustomerProfile.objects.get(account_number=acct.account_number)
            except CustomerProfile.DoesNotExist:
                form.add_error('account_number',"Invalid Account Number")
                context={'form':form}
                return render(request,"authenticate.html",context)
            else:
                #need to use tobytes(), model binaryfield is type memoryview. does not support read
                encrypted_account=bytes(account_in_db.account_encrypted)

                cycled_plaintext, decrypted_header = aws_encryption_sdk.decrypt(
                    source=encrypted_account,
                    key_provider=master_key_decryption_provider
                )
                encryption_context={'account_number':acct.account_number}
                encryption_context_passed=all(
                    pair in decrypted_header.encryption_context.items()
                    for pair in encryption_context.items()
                )
                if not encryption_context_passed:
                    #TODO encryption context doesn't match, some type of data tampering has occurred
                    #appropriate error logging and notify security operations center
                    form.add_error('account_number','Account number entered incorrectly')
                    context={'form':form}
                    return render(request,"authenticate.html",context)

                decrypted=cycled_plaintext.decode("utf-8")
                if acct.userid==decrypted:
                    return render(request,'authenticatesuccess.html',{})
                else:
                    form.add_error('account_number',"Account number entered incorrectly")
                    context={'form':form}
                    return render(request,"authenticate.html",context)

    if request.method=='GET':
        form=CustomerProfileForm()
        context={'form':form}
        return render(request,"authenticate.html",context)

