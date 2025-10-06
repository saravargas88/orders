######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################
# cspell: ignore= userid, backref
"""
Persistent Base class for database CRUD functions
"""

import logging
from datetime import date
from .persistent_base import db, PersistentBase, DataValidationError
from .address import Address

logger = logging.getLogger("flask.app")


######################################################################
#  O R D E R    M O D E L
######################################################################
class Order(db.Model, PersistentBase):
    """
    Class that represents an Order
    """

    # Table Schema
    #ORDER ID
    id = db.Column(db.Integer, primary_key=True)
    #USER ID
    userid = db.Column(db.String(16), nullable=False)
    #Order Address 
    #address= ???
    #STATUS OS ORDER
    status = db.Column(db.String(64), nullable=False, default = "PENDING")
    #DATE OF CREATION
    created_at= db.Column(db.Date(), nullable=False, default=date.today())
    #UPDATE DATE 
    updated_at= db.Column(db.Date(), nullable=False)
    #ITEMS IN ORDER
    items = db.relationship("Item", backref="order", passive_deletes=True)
    #SHIPPING ADDRESS which should be specified by accounts 
    shipping_address_id = db.Column(db.Integer, nullable=False)
   

    def __repr__(self):
        return f"<Order id=[{self.id}]>"

    def serialize(self):
    """Converts an Order instance into a dictionary."""
        Order = {
            "id": self.id,
            "userid": self.userid,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "shipping_address_id": self.shipping_address_id,
            "items": [],
        }

        # Serialize related items
        for item in self.items:
            order["items"].append(item.serialize())

    return order


    def deserialize(self, data):
        """
        Populates an Order from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id = data["id"]
            self.userid = data["userid"]
            self.email = data["email"]
            self.phone_number = data.get("phone_number")
            self.date_joined = date.fromisoformat(data["date_joined"])
            # handle inner list of addresses
            address_list = data.get("addresses")
            for json_address in address_list:
                address = Address()
                address.deserialize(json_address)
                self.addresses.append(address)
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Account: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Account: body of request contained bad or no data "
                + str(error)
            ) from error

        return self

    @classmethod
    def find_by_name(cls, name):
        """Returns all Accounts with the given name

        Args:
            name (string): the name of the Accounts you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
